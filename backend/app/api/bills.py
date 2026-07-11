"""Per-resident billing, privileged ledger entry, and verified Razorpay checkout."""
import json
import os
from typing import List, Optional

from fastapi import APIRouter, Depends, Header, HTTPException, Query, Request, status
from fastapi.responses import FileResponse
from sqlalchemy import desc, select
from sqlalchemy.orm import Session, selectinload

from app.core.config import settings
from app.core.deps import get_current_user, require_any_role
from app.db.base import get_db
from app.models.audit import AuditLog
from app.models.bill import Bill, BillStatus, PaymentAttempt, PaymentAttemptStatus, PaymentMethod
from app.models.resident import Resident
from app.models.society import Flat
from app.models.user import User
from app.schemas.bill import BillCreate, BillOut, PaymentCreate, PaymentOrderOut, PaymentOut, PaymentVerify
from app.services.billing_service import apply_late_fees_and_overdue, create_user_bill, record_payment
from app.services.razorpay_service import configured as razorpay_configured
from app.services.razorpay_service import create_order, verify_checkout_signature, verify_webhook_signature
from app.services.report_service import save_bill_pdf

router = APIRouter(prefix="/bills", tags=["bills"])
MANAGERS = {"admin", "committee"}


def _manager(user: User) -> bool: return user.is_superuser or bool(MANAGERS.intersection(user.role_names))


def _bill_query(): return select(Bill).options(selectinload(Bill.line_items), selectinload(Bill.payment_attempts), selectinload(Bill.billed_user))


def _get_bill(db: Session, bill_id: int) -> Bill:
    bill = db.execute(_bill_query().where(Bill.id == bill_id)).scalar_one_or_none()
    if not bill: raise HTTPException(status_code=404, detail="Bill not found")
    return bill


def _authorize_bill(user: User, bill: Bill) -> None:
    if bill.society_id != user.society_id or (not _manager(user) and bill.billed_user_id != user.id):
        raise HTTPException(status_code=403, detail="You cannot access this bill")


@router.get("/payment-config")
def payment_config(current=Depends(get_current_user)):
    return {"razorpay_enabled": razorpay_configured(), "currency": "INR", "method": "upi"}


@router.get("/", response_model=List[BillOut])
def list_bills(db: Session = Depends(get_db), current: User = Depends(get_current_user),
               status_filter: Optional[str] = Query(None, alias="status"), limit: int = Query(100, le=200)):
    if not current.society_id: return []
    query = _bill_query().where(Bill.society_id == current.society_id)
    if not _manager(current): query = query.where(Bill.billed_user_id == current.id)
    if status_filter:
        try: query = query.where(Bill.status == BillStatus(status_filter))
        except ValueError as exc: raise HTTPException(status_code=400, detail="Invalid bill status") from exc
    return [BillOut.model_validate(row) for row in db.execute(query.order_by(desc(Bill.issue_date)).limit(limit)).scalars().unique().all()]


@router.post("/", response_model=BillOut, status_code=201)
def create_bill(payload: BillCreate, db: Session = Depends(get_db), current: User = Depends(get_current_user)):
    require_any_role(current, ["admin"])
    user = db.get(User, payload.billed_user_id)
    if not user: raise HTTPException(status_code=404, detail="Resident not found")
    try:
        bill = create_user_bill(db, society_id=current.society_id, billed_user=user, **payload.model_dump(exclude={"billed_user_id"}))
    except ValueError as exc: raise HTTPException(status_code=409, detail=str(exc)) from exc
    db.add(AuditLog(actor_id=current.id, action="bill_created", entity_type="bill", entity_id=bill.id,
                    details=f"user={user.id};period={payload.billing_year}-{payload.billing_month:02d}")); db.commit()
    return BillOut.model_validate(_get_bill(db, bill.id))


@router.post("/sweep-overdue")
def sweep(db: Session = Depends(get_db), current: User = Depends(get_current_user)):
    require_any_role(current, ["admin", "committee"]); return {"updated": apply_late_fees_and_overdue(db, current.society_id)}


@router.post("/{bill_id}/manual-payment", response_model=PaymentOut, status_code=201)
def manual_payment(bill_id: int, payload: PaymentCreate, db: Session = Depends(get_db), current: User = Depends(get_current_user)):
    require_any_role(current, ["admin", "committee"]); bill = _get_bill(db, bill_id); _authorize_bill(current, bill)
    if payload.method not in {PaymentMethod.cash.value, PaymentMethod.cheque.value}:
        raise HTTPException(status_code=400, detail="Manual ledger entry supports cash or cheque only")
    try: payment = record_payment(db, bill, payload.amount, payload.method, payload.transaction_ref, current.id, payload.notes)
    except ValueError as exc: raise HTTPException(status_code=400, detail=str(exc)) from exc
    return PaymentOut.model_validate(payment)


@router.post("/{bill_id}/payment-order", response_model=PaymentOrderOut)
def payment_order(bill_id: int, db: Session = Depends(get_db), current: User = Depends(get_current_user)):
    bill = _get_bill(db, bill_id); _authorize_bill(current, bill)
    if bill.billed_user_id != current.id: raise HTTPException(status_code=403, detail="Only the billed resident can start UPI payment")
    if not razorpay_configured(): raise HTTPException(status_code=503, detail="Online UPI payment is not configured")
    if bill.outstanding <= 0: raise HTTPException(status_code=409, detail="Bill is already paid")
    amount_paise = int(round(bill.outstanding * 100))
    try: order = create_order(amount_paise=amount_paise, receipt=bill.bill_number,
        notes={"bill_id": str(bill.id), "user_id": str(current.id), "society_id": str(current.society_id)})
    except Exception as exc: raise HTTPException(status_code=502, detail="Payment provider could not create an order") from exc
    attempt = PaymentAttempt(bill_id=bill.id, user_id=current.id, amount=bill.outstanding,
        status=PaymentAttemptStatus.created, provider_order_id=order["id"])
    db.add(attempt); db.commit(); db.refresh(attempt)
    return PaymentOrderOut(attempt_id=attempt.id, order_id=order["id"], amount_paise=amount_paise,
        key_id=settings.RAZORPAY_KEY_ID, bill_number=bill.bill_number, resident_name=current.full_name)


@router.post("/payments/verify")
def verify_payment(payload: PaymentVerify, db: Session = Depends(get_db), current: User = Depends(get_current_user)):
    attempt = db.execute(select(PaymentAttempt).where(PaymentAttempt.provider_order_id == payload.razorpay_order_id)).scalar_one_or_none()
    if not attempt or attempt.user_id != current.id: raise HTTPException(status_code=404, detail="Payment attempt not found")
    if not verify_checkout_signature(payload.razorpay_order_id, payload.razorpay_payment_id, payload.razorpay_signature):
        raise HTTPException(status_code=400, detail="Invalid payment signature")
    attempt.provider_payment_id = payload.razorpay_payment_id; attempt.status = PaymentAttemptStatus.pending; db.commit()
    return {"status": "pending", "message": "Payment received and awaiting bank confirmation"}


@router.post("/payments/webhook", include_in_schema=False)
async def razorpay_webhook(request: Request, x_razorpay_signature: str = Header(""), db: Session = Depends(get_db)):
    raw = await request.body()
    if not verify_webhook_signature(raw, x_razorpay_signature): raise HTTPException(status_code=400, detail="Invalid webhook signature")
    payload = json.loads(raw); event = payload.get("event", ""); payment = payload.get("payload", {}).get("payment", {}).get("entity", {})
    order_id, payment_id = payment.get("order_id"), payment.get("id")
    if not order_id: return {"ok": True}
    attempt = db.execute(select(PaymentAttempt).where(PaymentAttempt.provider_order_id == order_id)).scalar_one_or_none()
    if not attempt: return {"ok": True}
    if event in {"payment.failed"}:
        attempt.status = PaymentAttemptStatus.failed; attempt.failure_reason = payment.get("error_description"); db.commit(); return {"ok": True}
    if event not in {"payment.captured", "order.paid"}: return {"ok": True}
    if attempt.status == PaymentAttemptStatus.captured: return {"ok": True}
    bill = db.get(Bill, attempt.bill_id)
    amount = round(float(payment.get("amount", 0)) / 100, 2)
    if not bill or amount != round(attempt.amount, 2) or amount > bill.outstanding:
        attempt.status = PaymentAttemptStatus.failed; attempt.failure_reason = "Provider amount did not match outstanding bill"; db.commit(); return {"ok": True}
    attempt.provider_payment_id = payment_id; attempt.status = PaymentAttemptStatus.captured; db.flush()
    record_payment(db, bill, amount, PaymentMethod.upi.value, payment_id, attempt.user_id, "Verified Razorpay capture")
    return {"ok": True}


@router.get("/{bill_id}/pdf")
def bill_pdf(bill_id: int, db: Session = Depends(get_db), current: User = Depends(get_current_user)):
    bill = _get_bill(db, bill_id); _authorize_bill(current, bill)
    flat = db.get(Flat, bill.flat_id); resident = db.get(User, bill.billed_user_id) if bill.billed_user_id else None
    path = os.path.join(os.path.abspath(settings.UPLOAD_DIR), f"{bill.bill_number}.pdf")
    save_bill_pdf(bill, f"{flat.number if flat else bill.flat_id}", resident.full_name if resident else "Resident")
    return FileResponse(path, media_type="application/pdf", filename=f"{bill.bill_number}.pdf")

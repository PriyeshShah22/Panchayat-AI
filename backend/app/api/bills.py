"""Bills + Payments router."""
import os
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import FileResponse
from sqlalchemy import desc, select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.deps import get_current_user, require_any_role
from app.db.base import get_db
from app.models.bill import Bill, BillStatus, PaymentMethod
from app.models.resident import Resident
from app.models.society import Flat
from app.models.user import User
from app.schemas.bill import BillCreate, BillOut, PaymentCreate, PaymentOut
from app.services.billing_service import (
    apply_late_fees_and_overdue,
    generate_monthly_bills,
    record_payment,
)
from app.services.report_service import generate_bill_pdf, save_bill_pdf

router = APIRouter(prefix="/bills", tags=["bills"])


def _flat_display(db: Session, bill: Bill) -> str:
    flat = db.get(Flat, bill.flat_id)
    if not flat:
        return f"Flat-{bill.flat_id}"
    return f"{flat.number} (Block {flat.block_id}, Floor {flat.floor})"


def _resident_display(db: Session, bill: Bill) -> str:
    if not bill.resident_id:
        return "Resident"
    res = db.get(Resident, bill.resident_id)
    if not res or not res.user:
        return "Resident"
    return res.user.full_name


@router.get("/", response_model=List[BillOut])
def list_bills(
    db: Session = Depends(get_db),
    current: User = Depends(get_current_user),
    status_filter: Optional[str] = Query(None, alias="status"),
    mine: bool = Query(False),
    limit: int = Query(50, le=200),
) -> list[BillOut]:
    q = select(Bill).order_by(desc(Bill.created_at))
    if current.is_superuser or "committee" in current.role_names or "admin" in current.role_names:
        pass
    elif mine or current.resident:
        flat_id = current.resident.flat_id if current.resident else None
        if flat_id is not None:
            q = q.where(Bill.flat_id == flat_id)
        else:
            q = q.where(Bill.resident_id == -1)  # no results
    if status_filter:
        try:
            q = q.where(Bill.status == BillStatus(status_filter))
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid status '{status_filter}'")
    rows = db.execute(q.limit(limit)).scalars().all()
    return [BillOut.model_validate(b) for b in rows]


@router.post("/", response_model=BillOut, status_code=status.HTTP_201_CREATED)
def create_bill(payload: BillCreate, db: Session = Depends(get_db),
                current=Depends(get_current_user)) -> BillOut:
    require_any_role(current, ["admin", "committee"])
    year = 2025  # placeholder; existing _next_bill_number replaced below
    # generate bill number
    last = db.execute(select(Bill).order_by(Bill.id.desc()).limit(1)).scalars().first()
    seq = (last.id + 1) if last else 1
    bill_number = f"BILL-{payload.society_id}-{year}-{seq:04d}"
    bill = Bill(
        **payload.model_dump(),
        late_fee=0.0,
        total_amount=payload.amount,
        paid_amount=0.0,
        status=BillStatus.pending,
        bill_number=bill_number,
    )
    db.add(bill)
    db.commit()
    db.refresh(bill)
    return BillOut.model_validate(bill)


@router.post("/generate-monthly", response_model=List[BillOut])
def generate_monthly(society_id: int, db: Session = Depends(get_db),
                     current=Depends(get_current_user)) -> list[BillOut]:
    require_any_role(current, ["admin", "committee"])
    rows = generate_monthly_bills(db, society_id)
    return [BillOut.model_validate(b) for b in rows]


@router.post("/sweep-overdue")
def sweep(society_id: Optional[int] = None, db: Session = Depends(get_db),
          current=Depends(get_current_user)) -> dict:
    require_any_role(current, ["admin", "committee"])
    n = apply_late_fees_and_overdue(db, society_id)
    return {"updated": n}


@router.post("/{bill_id}/pay", response_model=PaymentOut, status_code=status.HTTP_201_CREATED)
def pay(bill_id: int, payload: PaymentCreate, db: Session = Depends(get_db),
        current=Depends(get_current_user)) -> PaymentOut:
    bill = db.get(Bill, bill_id)
    if not bill:
        raise HTTPException(status_code=404, detail="Bill not found")
    # resident can only pay their own
    if not (current.is_superuser or "committee" in current.role_names or "admin" in current.role_names):
        if not current.resident or current.resident.flat_id != bill.flat_id:
            raise HTTPException(status_code=403, detail="Not your bill")
    try:
        method = PaymentMethod(payload.method)
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid method '{payload.method}'")
    payment = record_payment(db, bill, payload.amount, method.value,
                              payload.transaction_ref, current.id, payload.notes)
    return PaymentOut.model_validate(payment)


@router.get("/{bill_id}/pdf")
def bill_pdf(bill_id: int, db: Session = Depends(get_db),
             current=Depends(get_current_user)):
    bill = db.get(Bill, bill_id)
    if not bill:
        raise HTTPException(status_code=404, detail="Bill not found")
    if not (current.is_superuser or "committee" in current.role_names or "admin" in current.role_names):
        if not current.resident or current.resident.flat_id != bill.flat_id:
            raise HTTPException(status_code=403, detail="Not your bill")

    folder = os.path.abspath(settings.UPLOAD_DIR)
    path = os.path.join(folder, f"{bill.bill_number}.pdf")
    fd = _flat_display(db, bill)
    rd = _resident_display(db, bill)
    save_bill_pdf(bill, fd, rd)
    return FileResponse(path, media_type="application/pdf",
                        filename=f"{bill.bill_number}.pdf")

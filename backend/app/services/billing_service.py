"""Billing utilities: monthly bill generation, late fees, overdue sweep."""
from __future__ import annotations

from datetime import date, datetime, timedelta
from typing import List

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.bill import Bill, BillStatus, Payment
from app.models.resident import Resident
from app.models.society import Flat


def _next_bill_number(db: Session, society_id: int) -> str:
    year = datetime.utcnow().year
    prefix = f"BILL-{society_id}-{year}-"
    last = db.execute(
        select(Bill).where(Bill.bill_number.like(f"{prefix}%"))
        .order_by(Bill.id.desc()).limit(1)
    ).scalars().first()
    seq = 1
    if last and last.bill_number.startswith(prefix):
        try:
            seq = int(last.bill_number.split("-")[-1]) + 1
        except ValueError:
            seq = last.id + 1
    return f"{prefix}{seq:04d}"


def generate_monthly_bills(db: Session, society_id: int, period_label: str | None = None,
                           amount: float | None = None) -> List[Bill]:
    """Generate one monthly bill per flat for the given society.

    Idempotent: skips flats that already have a bill for the current calendar
    month — safe to call from seed scripts and the APScheduler monthly cron.
    """
    flats = db.execute(select(Flat).where(Flat.society_id == society_id)).scalars().all()
    today = date.today()
    month_start = datetime(today.year, today.month, 1)
    due = today + timedelta(days=15)
    period = period_label or today.strftime("%B %Y")
    amt = amount if amount is not None else settings.DEFAULT_MAINTENANCE_AMOUNT

    created: List[Bill] = []
    for flat in flats:
        # Skip if a bill already exists for this flat in the current month.
        existing = db.execute(
            select(Bill).where(
                Bill.flat_id == flat.id,
                Bill.created_at >= month_start,
                Bill.title.like(f"Maintenance {period}%"),
            ).limit(1)
        ).scalars().first()
        if existing:
            continue
        resident = db.execute(
            select(Resident).where(Resident.flat_id == flat.id)
        ).scalars().first()

        bill = Bill(
            society_id=society_id,
            flat_id=flat.id,
            resident_id=resident.id if resident else None,
            bill_number=_next_bill_number(db, society_id),
            title=f"Maintenance {period}",
            description=f"Monthly maintenance for {period}",
            amount=amt,
            late_fee=0.0,
            total_amount=amt,
            paid_amount=0.0,
            status=BillStatus.pending,
            issue_date=today,
            due_date=due,
        )
        db.add(bill)
        try:
            db.flush()
        except Exception:
            db.rollback()
            continue
        created.append(bill)
    db.commit()
    return created


def apply_late_fees_and_overdue(db: Session, society_id: int | None = None) -> int:
    """Mark past-due unpaid bills as overdue, apply late fees.

    Returns the number of bills updated.
    """
    today = date.today()
    q = select(Bill).where(Bill.status == BillStatus.pending, Bill.due_date < today)
    if society_id is not None:
        q = q.where(Bill.society_id == society_id)
    bills = db.execute(q).scalars().all()

    updated = 0
    for bill in bills:
        days_late = max(1, (today - bill.due_date).days)
        fee = round(bill.amount * (settings.LATE_FEE_PERCENT / 100.0) * (1 if days_late < 30 else 2), 2)
        if fee > bill.late_fee:
            bill.late_fee = fee
        bill.total_amount = bill.amount + bill.late_fee
        bill.status = BillStatus.overdue
        updated += 1
    db.commit()
    return updated


def record_payment(db: Session, bill: Bill, amount: float, method: str,
                   transaction_ref: str | None = None, received_by: int | None = None,
                   notes: str | None = None) -> Payment:
    """Record a payment against a bill and update bill state."""
    payment = Payment(
        bill_id=bill.id,
        amount=amount,
        method=method,
        transaction_ref=transaction_ref,
        received_by=received_by,
        notes=notes,
    )
    db.add(payment)
    bill.paid_amount = round(bill.paid_amount + amount, 2)
    bill.paid_at = datetime.utcnow()
    if bill.paid_amount >= bill.total_amount:
        bill.status = BillStatus.paid
    elif bill.paid_amount > 0:
        bill.status = BillStatus.partial
    db.commit()
    db.refresh(payment)
    return payment

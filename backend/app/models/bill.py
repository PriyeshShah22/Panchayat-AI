"""Maintenance bills and payments."""
from __future__ import annotations

import enum
from datetime import datetime
from typing import List, Optional

from sqlalchemy import Date, DateTime, Enum, Float, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class BillStatus(str, enum.Enum):
    pending = "pending"
    paid = "paid"
    overdue = "overdue"
    partial = "partial"
    cancelled = "cancelled"


class PaymentMethod(str, enum.Enum):
    cash = "cash"
    upi = "upi"
    card = "card"
    netbanking = "netbanking"
    cheque = "cheque"


class PaymentAttemptStatus(str, enum.Enum):
    created = "created"
    pending = "pending"
    captured = "captured"
    failed = "failed"
    abandoned = "abandoned"


class Bill(Base):
    __tablename__ = "bills"
    __table_args__ = (UniqueConstraint("billed_user_id", "billing_year", "billing_month", name="uq_bill_user_period"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    society_id: Mapped[int] = mapped_column(Integer, ForeignKey("societies.id", ondelete="CASCADE"), nullable=False, index=True)
    flat_id: Mapped[int] = mapped_column(Integer, ForeignKey("flats.id", ondelete="CASCADE"), nullable=False, index=True)
    resident_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("residents.id", ondelete="SET NULL"), nullable=True)
    billed_user_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=True, index=True)
    billing_year: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    billing_month: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    bill_number: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    amount: Mapped[float] = mapped_column(Float, nullable=False)
    late_fee: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    total_amount: Mapped[float] = mapped_column(Float, nullable=False)
    paid_amount: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)

    status: Mapped[BillStatus] = mapped_column(Enum(BillStatus), default=BillStatus.pending, nullable=False, index=True)
    issue_date: Mapped[datetime] = mapped_column(Date, default=datetime.utcnow, nullable=False)
    due_date: Mapped[datetime] = mapped_column(Date, nullable=False)
    paid_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    payments: Mapped[list["Payment"]] = relationship(
        "Payment", back_populates="bill", cascade="all, delete-orphan"
    )
    line_items: Mapped[List["BillLineItem"]] = relationship(
        "BillLineItem", back_populates="bill", cascade="all, delete-orphan", order_by="BillLineItem.id"
    )
    payment_attempts: Mapped[List["PaymentAttempt"]] = relationship(
        "PaymentAttempt", back_populates="bill", cascade="all, delete-orphan"
    )
    billed_user: Mapped[Optional["User"]] = relationship("User", foreign_keys=[billed_user_id])

    @property
    def outstanding(self) -> float:
        return round(self.total_amount - self.paid_amount, 2)


class Payment(Base):
    __tablename__ = "payments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    bill_id: Mapped[int] = mapped_column(Integer, ForeignKey("bills.id", ondelete="CASCADE"), nullable=False, index=True)
    amount: Mapped[float] = mapped_column(Float, nullable=False)
    method: Mapped[PaymentMethod] = mapped_column(Enum(PaymentMethod), default=PaymentMethod.upi, nullable=False)
    transaction_ref: Mapped[Optional[str]] = mapped_column(String(200))
    received_by: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    paid_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    bill: Mapped[Bill] = relationship(Bill, back_populates="payments")


class BillLineItem(Base):
    __tablename__ = "bill_line_items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    bill_id: Mapped[int] = mapped_column(Integer, ForeignKey("bills.id", ondelete="CASCADE"), nullable=False, index=True)
    code: Mapped[str] = mapped_column(String(40), nullable=False)
    label: Mapped[str] = mapped_column(String(120), nullable=False)
    amount: Mapped[float] = mapped_column(Float, nullable=False)
    bill: Mapped[Bill] = relationship(Bill, back_populates="line_items")


class PaymentAttempt(Base):
    __tablename__ = "payment_attempts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    bill_id: Mapped[int] = mapped_column(Integer, ForeignKey("bills.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    amount: Mapped[float] = mapped_column(Float, nullable=False)
    status: Mapped[PaymentAttemptStatus] = mapped_column(Enum(PaymentAttemptStatus), default=PaymentAttemptStatus.created, nullable=False, index=True)
    provider: Mapped[str] = mapped_column(String(30), default="razorpay", nullable=False)
    provider_order_id: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    provider_payment_id: Mapped[Optional[str]] = mapped_column(String(100), unique=True, index=True)
    failure_reason: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    bill: Mapped[Bill] = relationship(Bill, back_populates="payment_attempts")


from app.models.user import User  # noqa: E402

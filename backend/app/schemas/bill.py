"""Bill and Payment schemas."""
from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class BillCreate(BaseModel):
    society_id: int
    flat_id: int
    resident_id: Optional[int] = None
    title: str
    description: Optional[str] = None
    amount: float
    due_date: date


class BillOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    society_id: int
    flat_id: int
    resident_id: Optional[int] = None
    bill_number: str
    title: str
    description: Optional[str] = None
    amount: float
    late_fee: float
    total_amount: float
    paid_amount: float
    status: str
    issue_date: date
    due_date: date
    paid_at: Optional[datetime] = None
    created_at: datetime


class PaymentCreate(BaseModel):
    amount: float
    method: str = "upi"
    transaction_ref: Optional[str] = None
    notes: Optional[str] = None


class PaymentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    bill_id: int
    amount: float
    method: str
    transaction_ref: Optional[str] = None
    received_by: Optional[int] = None
    paid_at: datetime
    notes: Optional[str] = None

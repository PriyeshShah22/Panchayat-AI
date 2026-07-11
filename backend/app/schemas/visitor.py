"""Visitor schemas."""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class VisitorCreate(BaseModel):
    society_id: int
    flat_id: int
    name: str
    phone: Optional[str] = None
    purpose: Optional[str] = None
    id_proof_type: Optional[str] = None
    id_proof_number: Optional[str] = None
    photo_url: Optional[str] = None
    vehicle_number: Optional[str] = None
    expected_at: Optional[datetime] = None


class VisitorUpdate(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None
    purpose: Optional[str] = None


class VisitorActionRequest(BaseModel):
    action: str  # approve, reject, check_in, check_out
    note: Optional[str] = None


class VisitorOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    society_id: int
    flat_id: int
    host_id: int
    name: str
    phone: Optional[str] = None
    purpose: Optional[str] = None
    id_proof_type: Optional[str] = None
    id_proof_number: Optional[str] = None
    photo_url: Optional[str] = None
    vehicle_number: Optional[str] = None
    qr_code: Optional[str] = None
    status: str
    expected_at: Optional[datetime] = None
    created_at: datetime

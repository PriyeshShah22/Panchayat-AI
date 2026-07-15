"""Visitor schemas."""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_serializer


class VisitorCreate(BaseModel):
    society_id: int
    flat_id: int
    name: str = Field(min_length=2, max_length=150)
    phone: Optional[str] = Field(default=None, max_length=20)
    purpose: Optional[str] = Field(default=None, max_length=200)
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
    flat_number: Optional[str] = None
    wing_name: Optional[str] = None
    host_name: Optional[str] = None

    @field_serializer("expected_at", "created_at")
    def serialize_utc(self, value: Optional[datetime]) -> Optional[str]:
        if value is None:
            return None
        return value.isoformat(timespec="seconds") + ("Z" if value.tzinfo is None else "")

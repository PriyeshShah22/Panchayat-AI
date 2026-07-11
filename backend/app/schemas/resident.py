"""Resident schemas."""
from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class ResidentCreate(BaseModel):
    user_id: int
    flat_id: int
    occupation: Optional[str] = None
    emergency_contact_name: Optional[str] = None
    emergency_contact_phone: Optional[str] = None
    date_of_birth: Optional[date] = None
    ownership: str = "owner"
    notes: Optional[str] = None


class ResidentUpdate(BaseModel):
    flat_id: Optional[int] = None
    occupation: Optional[str] = None
    emergency_contact_name: Optional[str] = None
    emergency_contact_phone: Optional[str] = None
    date_of_birth: Optional[date] = None
    ownership: Optional[str] = None
    notes: Optional[str] = None


class ResidentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    user_id: int
    flat_id: int
    occupation: Optional[str] = None
    emergency_contact_name: Optional[str] = None
    emergency_contact_phone: Optional[str] = None
    date_of_birth: Optional[date] = None
    ownership: str
    notes: Optional[str] = None
    created_at: datetime

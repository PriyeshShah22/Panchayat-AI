"""Society, Block, Flat schemas."""
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict


class SocietyCreate(BaseModel):
    name: str
    address: str
    city: Optional[str] = None
    state: Optional[str] = None
    pincode: Optional[str] = None
    registration_no: Optional[str] = None
    contact_email: Optional[str] = None
    contact_phone: Optional[str] = None


class SocietyOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    address: str
    city: Optional[str] = None
    state: Optional[str] = None
    pincode: Optional[str] = None
    registration_no: Optional[str] = None
    contact_email: Optional[str] = None
    contact_phone: Optional[str] = None
    created_at: datetime


class BlockCreate(BaseModel):
    society_id: int
    name: str
    floors: int = 1


class BlockOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    society_id: int
    name: str
    floors: int


class FlatCreate(BaseModel):
    society_id: int
    block_id: int
    number: str
    floor: int = 0
    area_sqft: Optional[int] = None
    bedrooms: int = 1
    bathrooms: int = 1


class FlatOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    society_id: int
    block_id: int
    number: str
    floor: int
    area_sqft: Optional[int] = None
    bedrooms: int
    bathrooms: int

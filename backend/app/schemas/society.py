"""Society, Block, Flat schemas."""
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, field_validator

from app.services.location_service import floor_for_flat, is_valid_flat, is_valid_wing, normalize_flat, normalize_wing


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
    floors: int = 4

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str) -> str:
        value = normalize_wing(value)
        if not is_valid_wing(value):
            raise ValueError("Building must be Wing A, B, C, or D")
        return value

    @field_validator("floors")
    @classmethod
    def validate_floors(cls, value: int) -> int:
        if value != 4:
            raise ValueError("Each wing must have exactly 4 floors")
        return value


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

    @field_validator("number")
    @classmethod
    def validate_number(cls, value: str) -> str:
        value = normalize_flat(value)
        if not is_valid_flat(value):
            raise ValueError("Flat must be 101-104, 201-204, 301-304, or 401-404")
        return value


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
    block_name: str

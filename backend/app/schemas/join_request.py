from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

from app.services.location_service import is_valid_flat, is_valid_wing, normalize_flat, normalize_wing


class JoinRequestCreate(BaseModel):
    full_name: str = Field(min_length=2, max_length=150)
    email: EmailStr
    phone: Optional[str] = Field(default=None, max_length=20)
    date_of_birth: date
    password: str = Field(min_length=8, max_length=128)
    society_id: int
    building_name: str = Field(min_length=1, max_length=100)
    flat_number: str = Field(min_length=1, max_length=50)

    @field_validator("building_name")
    @classmethod
    def validate_building(cls, value: str) -> str:
        value = normalize_wing(value)
        if not is_valid_wing(value):
            raise ValueError("Building must be Wing A, B, C, or D")
        return value

    @field_validator("flat_number")
    @classmethod
    def validate_flat_number(cls, value: str) -> str:
        value = normalize_flat(value)
        if not is_valid_flat(value):
            raise ValueError("Flat must be 101-104, 201-204, 301-304, or 401-404")
        return value


class JoinRequestOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    full_name: str
    email: EmailStr
    phone: Optional[str] = None
    date_of_birth: date
    society_id: Optional[int] = None
    building_name: str
    flat_number: str
    status: str
    created_at: datetime
    reviewed_at: Optional[datetime] = None

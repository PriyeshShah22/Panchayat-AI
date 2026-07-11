"""Auth request/response schemas."""
from typing import List, Optional

from pydantic import BaseModel, EmailStr, Field
from app.schemas.user import UserOut


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6)


class RegisterRequest(BaseModel):
    email: EmailStr
    phone: Optional[str] = None
    full_name: str
    password: str = Field(min_length=8)
    society_id: Optional[int] = None
    role_names: List[str] = Field(default_factory=lambda: ["resident"])


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UserOut


class RefreshRequest(BaseModel):
    refresh_token: str


class PasswordChangeRequest(BaseModel):
    current_password: str
    new_password: str = Field(min_length=8)

"""Resident profile (1:1 with a User in the resident role)."""
from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy import Date, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Resident(Base):
    __tablename__ = "residents"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False, index=True
    )
    flat_id: Mapped[int] = mapped_column(Integer, ForeignKey("flats.id", ondelete="CASCADE"), nullable=False, index=True)

    occupation: Mapped[Optional[str]] = mapped_column(String(100))
    emergency_contact_name: Mapped[Optional[str]] = mapped_column(String(120))
    emergency_contact_phone: Mapped[Optional[str]] = mapped_column(String(20))
    date_of_birth: Mapped[Optional[datetime]] = mapped_column(Date, nullable=True)
    ownership: Mapped[str] = mapped_column(String(20), default="owner", nullable=False)  # owner | tenant
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    user: Mapped["User"] = relationship("User", back_populates="resident")
    flat: Mapped["Flat"] = relationship("Flat", back_populates="residents")


from app.models.user import User  # noqa: E402
from app.models.society import Flat  # noqa: E402

"""Visitors and visitor logs."""
from __future__ import annotations

import enum
from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.core.time import utc_now


class VisitorStatus(str, enum.Enum):
    pending = "pending"
    approved = "approved"
    rejected = "rejected"
    checked_in = "checked_in"
    checked_out = "checked_out"


class Visitor(Base):
    __tablename__ = "visitors"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    society_id: Mapped[int] = mapped_column(Integer, ForeignKey("societies.id", ondelete="CASCADE"), nullable=False, index=True)
    flat_id: Mapped[int] = mapped_column(Integer, ForeignKey("flats.id", ondelete="CASCADE"), nullable=False, index=True)
    host_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)

    name: Mapped[str] = mapped_column(String(150), nullable=False)
    phone: Mapped[Optional[str]] = mapped_column(String(20))
    purpose: Mapped[Optional[str]] = mapped_column(String(200))
    id_proof_type: Mapped[Optional[str]] = mapped_column(String(50))
    id_proof_number: Mapped[Optional[str]] = mapped_column(String(100))
    photo_url: Mapped[Optional[str]] = mapped_column(String(500))
    vehicle_number: Mapped[Optional[str]] = mapped_column(String(50))
    qr_code: Mapped[Optional[str]] = mapped_column(String(255), unique=True)
    status: Mapped[VisitorStatus] = mapped_column(Enum(VisitorStatus), default=VisitorStatus.pending, nullable=False, index=True)

    expected_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now, nullable=False)

    host: Mapped["User"] = relationship("User")
    flat: Mapped["Flat"] = relationship("Flat")
    logs: Mapped[list["VisitorLog"]] = relationship(
        "VisitorLog", back_populates="visitor", cascade="all, delete-orphan"
    )

    @property
    def flat_number(self) -> str:
        return self.flat.number

    @property
    def wing_name(self) -> str:
        return self.flat.block.name

    @property
    def host_name(self) -> str:
        return self.host.full_name


class VisitorLog(Base):
    __tablename__ = "visitor_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    visitor_id: Mapped[int] = mapped_column(Integer, ForeignKey("visitors.id", ondelete="CASCADE"), nullable=False, index=True)
    action: Mapped[str] = mapped_column(String(50), nullable=False)
    actor_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    note: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now, nullable=False)

    visitor: Mapped[Visitor] = relationship(Visitor, back_populates="logs")


from app.models.user import User  # noqa: E402
from app.models.society import Flat  # noqa: E402

"""Society, Block, and Flat models."""
from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Society(Base):
    __tablename__ = "societies"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    address: Mapped[str] = mapped_column(Text, nullable=False)
    city: Mapped[Optional[str]] = mapped_column(String(100))
    state: Mapped[Optional[str]] = mapped_column(String(100))
    pincode: Mapped[Optional[str]] = mapped_column(String(20))
    registration_no: Mapped[Optional[str]] = mapped_column(String(100), unique=True)
    contact_email: Mapped[Optional[str]] = mapped_column(String(255))
    contact_phone: Mapped[Optional[str]] = mapped_column(String(20))

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    users: Mapped[List["User"]] = relationship("User", back_populates="society", cascade="all, delete-orphan")
    blocks: Mapped[List["Block"]] = relationship("Block", back_populates="society", cascade="all, delete-orphan")
    flats: Mapped[List["Flat"]] = relationship(
        "Flat", back_populates="society", cascade="all, delete-orphan", viewonly=True
    )


class Block(Base):
    __tablename__ = "blocks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    society_id: Mapped[int] = mapped_column(Integer, ForeignKey("societies.id", ondelete="CASCADE"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    floors: Mapped[int] = mapped_column(Integer, default=1, nullable=False)

    society: Mapped[Society] = relationship(Society, back_populates="blocks")
    flats: Mapped[List["Flat"]] = relationship("Flat", back_populates="block", cascade="all, delete-orphan")


class Flat(Base):
    __tablename__ = "flats"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    society_id: Mapped[int] = mapped_column(Integer, ForeignKey("societies.id", ondelete="CASCADE"), nullable=False, index=True)
    block_id: Mapped[int] = mapped_column(Integer, ForeignKey("blocks.id", ondelete="CASCADE"), nullable=False, index=True)
    number: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    floor: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    area_sqft: Mapped[Optional[float]] = mapped_column(Integer, nullable=True)
    bedrooms: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    bathrooms: Mapped[int] = mapped_column(Integer, default=1, nullable=False)

    society: Mapped[Society] = relationship(Society, back_populates="flats")
    block: Mapped[Block] = relationship(Block, back_populates="flats")
    residents: Mapped[List["Resident"]] = relationship("Resident", back_populates="flat")


from app.models.user import User  # noqa: E402

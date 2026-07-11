"""Complaints: category, status, priority, comments, history."""
from __future__ import annotations

import enum
from datetime import datetime
from typing import List, Optional

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class ComplaintStatus(str, enum.Enum):
    open = "open"
    in_progress = "in_progress"
    resolved = "resolved"
    closed = "closed"
    escalated = "escalated"


class ComplaintPriority(str, enum.Enum):
    low = "low"
    medium = "medium"
    high = "high"
    urgent = "urgent"


class ComplaintCategory(Base):
    __tablename__ = "complaint_categories"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    color: Mapped[Optional[str]] = mapped_column(String(7), default="#1976d2")

    complaints: Mapped[List["Complaint"]] = relationship("Complaint", back_populates="category")


class Complaint(Base):
    __tablename__ = "complaints"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    society_id: Mapped[int] = mapped_column(Integer, ForeignKey("societies.id", ondelete="CASCADE"), nullable=False, index=True)
    flat_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("flats.id", ondelete="SET NULL"), nullable=True)

    reporter_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    assignee_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)

    category_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("complaint_categories.id", ondelete="SET NULL"), nullable=True)
    status: Mapped[ComplaintStatus] = mapped_column(Enum(ComplaintStatus), default=ComplaintStatus.open, nullable=False, index=True)
    priority: Mapped[ComplaintPriority] = mapped_column(Enum(ComplaintPriority), default=ComplaintPriority.medium, nullable=False, index=True)

    photo_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    ai_suggested_category: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    resolved_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    reporter: Mapped["User"] = relationship(
        "User", back_populates="complaints", foreign_keys=[reporter_id]
    )
    assignee: Mapped[Optional["User"]] = relationship("User", foreign_keys=[assignee_id])
    category: Mapped[Optional[ComplaintCategory]] = relationship(ComplaintCategory, back_populates="complaints")
    comments: Mapped[List["ComplaintComment"]] = relationship(
        "ComplaintComment", back_populates="complaint", cascade="all, delete-orphan"
    )


class ComplaintComment(Base):
    __tablename__ = "complaint_comments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    complaint_id: Mapped[int] = mapped_column(Integer, ForeignKey("complaints.id", ondelete="CASCADE"), nullable=False, index=True)
    author_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    comment: Mapped[str] = mapped_column(Text, nullable=False)
    is_internal: Mapped[bool] = mapped_column(default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    complaint: Mapped[Complaint] = relationship(Complaint, back_populates="comments")
    author: Mapped["User"] = relationship("User")


from app.models.user import User  # noqa: E402

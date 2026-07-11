"""Complaint schemas."""
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict


class CategoryCreate(BaseModel):
    name: str
    description: Optional[str] = None
    color: Optional[str] = "#1976d2"


class CategoryOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    description: Optional[str] = None
    color: Optional[str] = None


class ComplaintCreate(BaseModel):
    title: str
    description: str
    society_id: int
    flat_id: Optional[int] = None
    category_id: Optional[int] = None
    priority: str = "medium"
    photo_url: Optional[str] = None


class ComplaintUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    priority: Optional[str] = None
    assignee_id: Optional[int] = None
    category_id: Optional[int] = None


class ComplaintOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    title: str
    description: str
    society_id: int
    flat_id: Optional[int] = None
    reporter_id: int
    assignee_id: Optional[int] = None
    category_id: Optional[int] = None
    status: str
    priority: str
    photo_url: Optional[str] = None
    ai_suggested_category: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    resolved_at: Optional[datetime] = None


class ComplaintCommentCreate(BaseModel):
    comment: str
    is_internal: bool = False


class ComplaintCommentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    complaint_id: int
    author_id: int
    comment: str
    is_internal: bool
    created_at: datetime

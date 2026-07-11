"""Notice schemas."""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class NoticeCreate(BaseModel):
    society_id: int
    title: str
    body: str
    is_pinned: bool = False
    audience: str = "all"
    expires_at: Optional[datetime] = None


class NoticeOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    society_id: int
    author_id: int
    title: str
    body: str
    is_pinned: bool
    audience: str
    published_at: datetime
    expires_at: Optional[datetime] = None

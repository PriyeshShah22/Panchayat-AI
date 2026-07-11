"""Chat (AI assistant) schemas."""
from datetime import datetime
from typing import Any, List, Literal, Optional

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=2000)
    language: str = Field(default="en", max_length=12)
    history: Optional[List[dict]] = None  # [{"role": "user"|"assistant", "content": "..."}]


class ChatResponse(BaseModel):
    intent: Optional[str] = None
    reply: str
    data: Optional[dict] = None
    action: Optional["ActionProposal"] = None
    available_actions: List[str] = Field(default_factory=list)
    input_transcript: Optional[str] = None
    detected_language: Optional[str] = None


class ActionProposal(BaseModel):
    id: int
    action_type: str
    risk: Literal["low", "medium", "high"]
    status: str
    summary: str
    fields: dict[str, Any]
    expires_at: datetime


class ActionResult(BaseModel):
    action_id: int
    status: str
    message: str
    entity_type: Optional[str] = None
    entity_id: Optional[int] = None

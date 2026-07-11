"""Chat (AI assistant) schemas."""
from typing import List, Optional

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    message: str = Field(min_length=1)
    history: Optional[List[dict]] = None  # [{"role": "user"|"assistant", "content": "..."}]


class ChatResponse(BaseModel):
    intent: Optional[str] = None
    reply: str
    data: Optional[dict] = None

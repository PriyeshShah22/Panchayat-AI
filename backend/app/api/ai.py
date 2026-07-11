"""AI assistant endpoint."""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.db.base import get_db
from app.models.user import User
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.ai_service import chat as ai_chat

router = APIRouter(prefix="/ai", tags=["ai"])


@router.post("/chat", response_model=ChatResponse)
def chat(payload: ChatRequest,
         db: Session = Depends(get_db),
         current: User = Depends(get_current_user)) -> ChatResponse:
    result = ai_chat(db, current, payload.message)
    return ChatResponse(**result)

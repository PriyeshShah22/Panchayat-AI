"""AI assistant endpoint."""
import json
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from openai import APIConnectionError, APIStatusError, RateLimitError
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.db.base import get_db
from app.models.user import User
from app.schemas.chat import ActionResult, ChatRequest, ChatResponse
from app.services.ai_service import cancel_action, chat as ai_chat, confirm_action
from app.services.sarvam_service import SarvamUnavailable, translate_audio

router = APIRouter(prefix="/ai", tags=["ai"])


@router.post("/chat", response_model=ChatResponse)
def chat(payload: ChatRequest,
         db: Session = Depends(get_db),
         current: User = Depends(get_current_user)) -> ChatResponse:
    try:
        result = ai_chat(db, current, payload.message, payload.language, payload.history, payload.conversation_summary)
        return ChatResponse(**result)
    except RateLimitError as exc:
        raise HTTPException(status_code=429, detail="The AI service is busy. Please try again shortly.") from exc
    except (APIConnectionError, APIStatusError) as exc:
        raise HTTPException(status_code=503, detail="The AI service is temporarily unavailable. Manual services still work.") from exc


@router.post("/voice", response_model=ChatResponse)
async def voice(
    audio: UploadFile = File(...),
    language: str = Form("unknown"),
    history: str = Form("[]"),
    conversation_summary: str = Form(""),
    db: Session = Depends(get_db),
    current: User = Depends(get_current_user),
) -> ChatResponse:
    content_type = (audio.content_type or "application/octet-stream").lower()
    raw = await audio.read()
    try:
        translated = translate_audio(raw, audio.filename or "recording.webm", content_type, language)
        try:
            parsed_history = json.loads(history)
        except json.JSONDecodeError as exc:
            raise ValueError("Invalid conversation history.") from exc
        result = ai_chat(db, current, translated["transcript"], translated["language_code"], parsed_history, conversation_summary or None)
        result["input_transcript"] = translated["transcript"]
        result["detected_language"] = translated["language_code"]
        return ChatResponse(**result)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except SarvamUnavailable as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except RateLimitError as exc:
        raise HTTPException(status_code=429, detail="The AI service is busy. Please try again shortly.") from exc
    except (APIConnectionError, APIStatusError) as exc:
        raise HTTPException(status_code=503, detail="The AI service is temporarily unavailable. Manual services still work.") from exc


@router.post("/actions/{action_id}/confirm", response_model=ActionResult)
def confirm(action_id: int, db: Session = Depends(get_db), current: User = Depends(get_current_user)):
    try:
        return ActionResult(**confirm_action(db, current, action_id))
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except PermissionError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc
    except TimeoutError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc


@router.post("/actions/{action_id}/cancel", response_model=ActionResult)
def cancel(action_id: int, db: Session = Depends(get_db), current: User = Depends(get_current_user)):
    try:
        return ActionResult(**cancel_action(db, current, action_id))
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except PermissionError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc

"""Permission-safe complaint workflow."""
from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import desc, select
from sqlalchemy.orm import Session, selectinload

from app.core.deps import get_current_user, require_any_role
from app.db.base import get_db
from app.models.audit import AuditLog
from app.models.complaint import Complaint, ComplaintCategory, ComplaintComment, ComplaintEvent, ComplaintPriority, ComplaintStatus
from app.models.user import User
from app.schemas.complaint import (CategoryCreate, CategoryOut, ComplaintCommentCreate,
    ComplaintCommentOut, ComplaintCreate, ComplaintOut, ComplaintTransition, ComplaintUpdate)
from app.services.complaint_service import classify_complaint, create_complaint as create_complaint_service

router = APIRouter(prefix="/complaints", tags=["complaints"])
MANAGER_ROLES = {"admin", "committee"}
TERMINAL = {ComplaintStatus.rejected, ComplaintStatus.resolved, ComplaintStatus.withdrawn}


def _manager(user: User) -> bool:
    return user.is_superuser or bool(MANAGER_ROLES.intersection(user.role_names))


def _can_view(user: User, complaint: Complaint) -> bool:
    return bool(user.society_id and user.society_id == complaint.society_id and (_manager(user) or complaint.reporter_id == user.id))


def _load(db: Session, complaint_id: int) -> Complaint:
    complaint = db.execute(select(Complaint).options(
        selectinload(Complaint.reporter), selectinload(Complaint.assignee),
        selectinload(Complaint.category), selectinload(Complaint.events),
    ).where(Complaint.id == complaint_id)).scalar_one_or_none()
    if not complaint:
        raise HTTPException(status_code=404, detail="Complaint not found")
    return complaint


def _out(complaint: Complaint) -> ComplaintOut:
    return ComplaintOut.model_validate(complaint)


@router.get("/categories", response_model=List[CategoryOut])
def list_categories(db: Session = Depends(get_db), current=Depends(get_current_user)):
    return [CategoryOut.model_validate(row) for row in db.execute(select(ComplaintCategory)).scalars().all()]


@router.post("/categories", response_model=CategoryOut, status_code=201)
def create_category(payload: CategoryCreate, db: Session = Depends(get_db), current=Depends(get_current_user)):
    require_any_role(current, ["admin", "committee"])
    if db.execute(select(ComplaintCategory).where(ComplaintCategory.name == payload.name)).scalar_one_or_none():
        raise HTTPException(status_code=409, detail="Category already exists")
    category = ComplaintCategory(**payload.model_dump()); db.add(category); db.commit(); db.refresh(category)
    return CategoryOut.model_validate(category)


@router.post("/classify")
def classify(payload: dict, current=Depends(get_current_user)):
    return {"suggested_category": classify_complaint(str(payload.get("text", "")))}


@router.post("/", response_model=ComplaintOut, status_code=201)
def create_complaint(payload: ComplaintCreate, db: Session = Depends(get_db), current: User = Depends(get_current_user)):
    try:
        complaint = create_complaint_service(db, current, payload, source="manual")
    except PermissionError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return _out(_load(db, complaint.id))


@router.get("/", response_model=List[ComplaintOut])
def list_complaints(db: Session = Depends(get_db), current: User = Depends(get_current_user),
                    status_filter: Optional[str] = Query(None, alias="status"), search: Optional[str] = None,
                    limit: int = Query(100, le=200)):
    if not current.society_id:
        return []
    query = select(Complaint).options(selectinload(Complaint.reporter), selectinload(Complaint.assignee),
        selectinload(Complaint.category), selectinload(Complaint.events)).where(Complaint.society_id == current.society_id)
    if not _manager(current):
        query = query.where(Complaint.reporter_id == current.id)
    if status_filter:
        try: query = query.where(Complaint.status == ComplaintStatus(status_filter))
        except ValueError as exc: raise HTTPException(status_code=400, detail="Invalid complaint status") from exc
    if search:
        like = f"%{search.strip()}%"; query = query.where(Complaint.title.ilike(like) | Complaint.description.ilike(like))
    rows = db.execute(query.order_by(desc(Complaint.created_at)).limit(limit)).scalars().unique().all()
    return [_out(row) for row in rows]


@router.get("/{complaint_id}", response_model=ComplaintOut)
def get_complaint(complaint_id: int, db: Session = Depends(get_db), current: User = Depends(get_current_user)):
    complaint = _load(db, complaint_id)
    if not _can_view(current, complaint): raise HTTPException(status_code=403, detail="You cannot view this complaint")
    return _out(complaint)


@router.patch("/{complaint_id}", response_model=ComplaintOut)
def update_complaint(complaint_id: int, payload: ComplaintUpdate, db: Session = Depends(get_db), current: User = Depends(get_current_user)):
    require_any_role(current, ["admin", "committee"]); complaint = _load(db, complaint_id)
    if complaint.society_id != current.society_id: raise HTTPException(status_code=403, detail="Different society")
    data = payload.model_dump(exclude_unset=True)
    if "priority" in data:
        try: complaint.priority = ComplaintPriority(data.pop("priority"))
        except ValueError as exc: raise HTTPException(status_code=400, detail="Invalid priority") from exc
    if data.get("assignee_id"):
        assignee = db.get(User, data["assignee_id"])
        if not assignee or assignee.society_id != current.society_id: raise HTTPException(status_code=400, detail="Invalid assignee")
    for key, value in data.items(): setattr(complaint, key, value)
    db.add(AuditLog(actor_id=current.id, action="complaint_details_updated", entity_type="complaint", entity_id=complaint.id))
    db.commit(); return _out(_load(db, complaint.id))


@router.post("/{complaint_id}/transition", response_model=ComplaintOut)
def transition(complaint_id: int, payload: ComplaintTransition, db: Session = Depends(get_db), current: User = Depends(get_current_user)):
    require_any_role(current, ["admin", "committee"]); complaint = _load(db, complaint_id)
    if complaint.society_id != current.society_id: raise HTTPException(status_code=403, detail="Different society")
    try: target = ComplaintStatus(payload.status)
    except ValueError as exc: raise HTTPException(status_code=400, detail="Invalid complaint status") from exc
    if target not in {ComplaintStatus.in_progress, ComplaintStatus.rejected, ComplaintStatus.resolved}:
        raise HTTPException(status_code=400, detail="Managers may choose In Progress, Rejected, or Resolved")
    if complaint.status in TERMINAL: raise HTTPException(status_code=409, detail="This complaint is already final")
    if target == ComplaintStatus.rejected and not (payload.reason or "").strip():
        raise HTTPException(status_code=422, detail="A rejection reason is required")
    previous = complaint.status; complaint.status = target
    complaint.resolved_at = datetime.utcnow() if target == ComplaintStatus.resolved else None
    db.add(ComplaintEvent(complaint_id=complaint.id, actor_id=current.id, from_status=previous.value,
                          to_status=target.value, reason=(payload.reason or "").strip() or None))
    db.add(AuditLog(actor_id=current.id, action="complaint_transition", entity_type="complaint", entity_id=complaint.id,
                    details=f"{previous.value}->{target.value}"))
    db.commit(); return _out(_load(db, complaint.id))


@router.post("/{complaint_id}/withdraw", response_model=ComplaintOut)
def withdraw(complaint_id: int, payload: ComplaintTransition, db: Session = Depends(get_db), current: User = Depends(get_current_user)):
    complaint = _load(db, complaint_id)
    if complaint.reporter_id != current.id or complaint.society_id != current.society_id: raise HTTPException(status_code=403, detail="Not your complaint")
    if complaint.status not in {ComplaintStatus.submitted, ComplaintStatus.in_progress}: raise HTTPException(status_code=409, detail="This complaint can no longer be withdrawn")
    previous = complaint.status; complaint.status = ComplaintStatus.withdrawn
    db.add(ComplaintEvent(complaint_id=complaint.id, actor_id=current.id, from_status=previous.value,
                          to_status=ComplaintStatus.withdrawn.value, reason=(payload.reason or "").strip() or "Withdrawn by resident"))
    db.add(AuditLog(actor_id=current.id, action="complaint_withdrawn", entity_type="complaint", entity_id=complaint.id))
    db.commit(); return _out(_load(db, complaint.id))


@router.post("/{complaint_id}/comments", response_model=ComplaintCommentOut, status_code=201)
def add_comment(complaint_id: int, payload: ComplaintCommentCreate, db: Session = Depends(get_db), current: User = Depends(get_current_user)):
    complaint = _load(db, complaint_id)
    if not _can_view(current, complaint): raise HTTPException(status_code=403, detail="You cannot comment on this complaint")
    if payload.is_internal and not _manager(current): raise HTTPException(status_code=403, detail="Only managers may add internal notes")
    comment = ComplaintComment(complaint_id=complaint_id, author_id=current.id, comment=payload.comment, is_internal=payload.is_internal)
    db.add(comment); db.commit(); db.refresh(comment); return ComplaintCommentOut.model_validate(comment)


@router.get("/{complaint_id}/comments", response_model=List[ComplaintCommentOut])
def list_comments(complaint_id: int, db: Session = Depends(get_db), current: User = Depends(get_current_user)):
    complaint = _load(db, complaint_id)
    if not _can_view(current, complaint): raise HTTPException(status_code=403, detail="You cannot view these comments")
    query = select(ComplaintComment).where(ComplaintComment.complaint_id == complaint_id)
    if not _manager(current): query = query.where(ComplaintComment.is_internal.is_(False))
    return [ComplaintCommentOut.model_validate(row) for row in db.execute(query.order_by(ComplaintComment.created_at)).scalars().all()]

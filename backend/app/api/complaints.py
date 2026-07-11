"""Complaints router."""
from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel
from sqlalchemy import desc, select
from sqlalchemy.orm import Session, selectinload

from app.core.deps import get_current_user, require_any_role
from app.db.base import get_db
from app.models.complaint import (
    Complaint,
    ComplaintCategory,
    ComplaintComment,
    ComplaintPriority,
    ComplaintStatus,
)
from app.models.audit import AuditLog
from app.models.user import User
from app.schemas.complaint import (
    CategoryCreate,
    CategoryOut,
    ComplaintCommentCreate,
    ComplaintCommentOut,
    ComplaintCreate,
    ComplaintOut,
    ComplaintUpdate,
)
from app.services.ai_service import classify_complaint

router = APIRouter(prefix="/complaints", tags=["complaints"])


def _ensure_known(name: str, enum_cls):
    try:
        return enum_cls(name)
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid value '{name}'")


@router.get("/categories", response_model=List[CategoryOut])
def list_categories(db: Session = Depends(get_db),
                    current=Depends(get_current_user)) -> list[CategoryOut]:
    rows = db.execute(select(ComplaintCategory)).scalars().all()
    return [CategoryOut.model_validate(c) for c in rows]


@router.post("/categories", response_model=CategoryOut, status_code=status.HTTP_201_CREATED)
def create_category(payload: CategoryCreate, db: Session = Depends(get_db),
                    current=Depends(get_current_user)) -> CategoryOut:
    require_any_role(current, ["admin", "committee"])
    existing = db.execute(select(ComplaintCategory)
                          .where(ComplaintCategory.name == payload.name)).scalar_one_or_none()
    if existing:
        raise HTTPException(status_code=400, detail="Category already exists")
    cat = ComplaintCategory(**payload.model_dump())
    db.add(cat)
    db.commit()
    db.refresh(cat)
    return CategoryOut.model_validate(cat)


@router.post("/classify")
def classify(payload: dict, current=Depends(get_current_user)) -> dict:
    text = payload.get("text", "")
    return {"suggested_category": classify_complaint(text)}


@router.post("/", response_model=ComplaintOut, status_code=status.HTTP_201_CREATED)
def create_complaint(payload: ComplaintCreate, db: Session = Depends(get_db),
                     current=Depends(get_current_user)) -> ComplaintOut:
    priority = _ensure_known(payload.priority, ComplaintPriority)

    suggested = None
    if payload.category_id is None:
        suggested = classify_complaint(payload.title + " " + payload.description)
        match = db.execute(select(ComplaintCategory)
                          .where(ComplaintCategory.name == suggested)).scalar_one_or_none()
        if match:
            category_id = match.id
        else:
            category_id = None
    else:
        category_id = payload.category_id

    comp = Complaint(
        title=payload.title,
        description=payload.description,
        society_id=payload.society_id,
        flat_id=payload.flat_id,
        reporter_id=current.id,
        category_id=category_id,
        priority=priority,
        status=ComplaintStatus.open,
        photo_url=payload.photo_url,
        ai_suggested_category=suggested,
    )
    db.add(comp)
    db.commit()
    db.refresh(comp)
    db.add(AuditLog(actor_id=current.id, action="complaint_create",
                    entity_type="complaint", entity_id=comp.id))
    db.commit()
    return ComplaintOut.model_validate(comp)


@router.get("/", response_model=List[ComplaintOut])
def list_complaints(
    db: Session = Depends(get_db),
    current: User = Depends(get_current_user),
    status_filter: Optional[str] = Query(None, alias="status"),
    mine: bool = Query(False),
    search: Optional[str] = None,
    limit: int = Query(50, le=200),
) -> list[ComplaintOut]:
    q = select(Complaint).options(selectinload(Complaint.category)).order_by(desc(Complaint.created_at))
    if current.is_superuser or "committee" in current.role_names or "admin" in current.role_names:
        pass
    elif mine:
        q = q.where(Complaint.reporter_id == current.id)
    else:
        q = q.where(Complaint.reporter_id == current.id)
    if status_filter:
        q = q.where(Complaint.status == _ensure_known(status_filter, ComplaintStatus))
    if search:
        like = f"%{search}%"
        q = q.where((Complaint.title.ilike(like)) | (Complaint.description.ilike(like)))
    rows = db.execute(q.limit(limit)).scalars().all()
    return [ComplaintOut.model_validate(c) for c in rows]


@router.get("/{complaint_id}", response_model=ComplaintOut)
def get_complaint(complaint_id: int, db: Session = Depends(get_db),
                  current=Depends(get_current_user)) -> ComplaintOut:
    comp = db.get(Complaint, complaint_id)
    if not comp:
        raise HTTPException(status_code=404, detail="Not found")
    if (not current.is_superuser
            and "committee" not in current.role_names
            and "admin" not in current.role_names
            and comp.reporter_id != current.id):
        raise HTTPException(status_code=403, detail="Not your complaint")
    return ComplaintOut.model_validate(comp)


@router.patch("/{complaint_id}", response_model=ComplaintOut)
def update_complaint(complaint_id: int, payload: ComplaintUpdate,
                     db: Session = Depends(get_db),
                     current=Depends(get_current_user)) -> ComplaintOut:
    comp = db.get(Complaint, complaint_id)
    if not comp:
        raise HTTPException(status_code=404, detail="Not found")
    if (not current.is_superuser
            and "committee" not in current.role_names
            and "admin" not in current.role_names
            and comp.reporter_id != current.id):
        raise HTTPException(status_code=403, detail="Forbidden")
    data = payload.model_dump(exclude_unset=True)
    if "status" in data:
        comp.status = _ensure_known(data.pop("status"), ComplaintStatus)
        if comp.status == ComplaintStatus.resolved:
            comp.resolved_at = datetime.utcnow()
    if "priority" in data:
        comp.priority = _ensure_known(data.pop("priority"), ComplaintPriority)
    for k, v in data.items():
        setattr(comp, k, v)
    db.commit()
    db.refresh(comp)
    db.add(AuditLog(actor_id=current.id, action="complaint_update",
                    entity_type="complaint", entity_id=comp.id,
                    details=f"status={comp.status.value}"))
    db.commit()
    return ComplaintOut.model_validate(comp)


@router.post("/{complaint_id}/comments", response_model=ComplaintCommentOut,
             status_code=status.HTTP_201_CREATED)
def add_comment(complaint_id: int, payload: ComplaintCommentCreate,
                db: Session = Depends(get_db),
                current=Depends(get_current_user)) -> ComplaintCommentOut:
    comp = db.get(Complaint, complaint_id)
    if not comp:
        raise HTTPException(status_code=404, detail="Not found")
    c = ComplaintComment(complaint_id=complaint_id, author_id=current.id,
                         comment=payload.comment, is_internal=payload.is_internal)
    db.add(c)
    db.commit()
    db.refresh(c)
    return ComplaintCommentOut.model_validate(c)


@router.get("/{complaint_id}/comments", response_model=List[ComplaintCommentOut])
def list_comments(complaint_id: int, db: Session = Depends(get_db),
                  current=Depends(get_current_user)) -> list[ComplaintCommentOut]:
    comp = db.get(Complaint, complaint_id)
    if not comp:
        raise HTTPException(status_code=404, detail="Not found")
    rows = db.execute(
        select(ComplaintComment).where(ComplaintComment.complaint_id == complaint_id)
        .order_by(ComplaintComment.created_at)
    ).scalars().all()
    if not current.is_superuser and "committee" not in current.role_names and "admin" not in current.role_names:
        rows = [r for r in rows if not r.is_internal or r.author_id == current.id]
    return [ComplaintCommentOut.model_validate(c) for c in rows]

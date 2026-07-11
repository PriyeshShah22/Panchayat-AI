"""Visitors router."""
import secrets
from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import desc, select
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, require_any_role
from app.db.base import get_db
from app.models.audit import AuditLog
from app.models.user import User
from app.models.visitor import Visitor, VisitorLog, VisitorStatus
from app.schemas.visitor import VisitorActionRequest, VisitorCreate, VisitorOut, VisitorUpdate

router = APIRouter(prefix="/visitors", tags=["visitors"])


def _ensure_status(name: str) -> VisitorStatus:
    try:
        return VisitorStatus(name)
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid visitor status '{name}'")


@router.post("/", response_model=VisitorOut, status_code=status.HTTP_201_CREATED)
def register_visitor(payload: VisitorCreate, db: Session = Depends(get_db),
                     current=Depends(get_current_user)) -> VisitorOut:
    visitor = Visitor(
        **payload.model_dump(),
        host_id=current.id,
        qr_code=secrets.token_urlsafe(12),
        status=VisitorStatus.pending,
    )
    db.add(visitor)
    db.commit()
    db.refresh(visitor)
    db.add(AuditLog(actor_id=current.id, action="visitor_register", entity_type="visitor",
                    entity_id=visitor.id))
    db.commit()
    return VisitorOut.model_validate(visitor)


@router.get("/", response_model=List[VisitorOut])
def list_visitors(
    db: Session = Depends(get_db),
    current: User = Depends(get_current_user),
    society_id: Optional[int] = None,
    mine: bool = Query(False),
    limit: int = Query(50, le=200),
) -> list[VisitorOut]:
    q = select(Visitor).order_by(desc(Visitor.created_at))
    if current.is_superuser or "security" in current.role_names or "committee" in current.role_names or "admin" in current.role_names:
        pass
    elif mine:
        q = q.where(Visitor.host_id == current.id)
    else:
        q = q.where(Visitor.host_id == current.id)
    if society_id is not None:
        q = q.where(Visitor.society_id == society_id)
    rows = db.execute(q.limit(limit)).scalars().all()
    return [VisitorOut.model_validate(v) for v in rows]


@router.patch("/{visitor_id}", response_model=VisitorOut)
def update_visitor(visitor_id: int, payload: VisitorUpdate,
                   db: Session = Depends(get_db),
                   current=Depends(get_current_user)) -> VisitorOut:
    v = db.get(Visitor, visitor_id)
    if not v:
        raise HTTPException(status_code=404, detail="Visitor not found")
    if v.host_id != current.id and not (current.is_superuser
                                        or "committee" in current.role_names
                                        or "security" in current.role_names
                                        or "admin" in current.role_names):
        raise HTTPException(status_code=403, detail="Forbidden")
    for k, val in payload.model_dump(exclude_unset=True).items():
        setattr(v, k, val)
    db.commit()
    db.refresh(v)
    return VisitorOut.model_validate(v)


@router.post("/{visitor_id}/action", response_model=VisitorOut)
def take_action(visitor_id: int, payload: VisitorActionRequest,
                db: Session = Depends(get_db),
                current=Depends(get_current_user)) -> VisitorOut:
    v = db.get(Visitor, visitor_id)
    if not v:
        raise HTTPException(status_code=404, detail="Visitor not found")
    action = payload.action.lower()
    mapping = {
        "approve": VisitorStatus.approved,
        "reject": VisitorStatus.rejected,
        "check_in": VisitorStatus.checked_in,
        "check_out": VisitorStatus.checked_out,
    }
    if action not in mapping:
        raise HTTPException(status_code=400, detail=f"Invalid action '{action}'")

    if action in ("approve", "reject"):
        if v.host_id != current.id and not (current.is_superuser or "committee" in current.role_names or "admin" in current.role_names):
            raise HTTPException(status_code=403, detail="Only host can approve/reject")
    else:
        require_any_role(current, ["security", "committee", "admin"])

    v.status = mapping[action]
    db.add(VisitorLog(visitor_id=v.id, action=action, actor_id=current.id, note=payload.note))
    db.add(AuditLog(actor_id=current.id, action=f"visitor_{action}", entity_type="visitor",
                    entity_id=v.id, details=payload.note))
    db.commit()
    db.refresh(v)
    return VisitorOut.model_validate(v)

"""Visitors router."""
import secrets
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
from app.core.time import as_utc_naive
from app.services.location_service import is_valid_flat, is_valid_wing
from app.services.notification_service import notify_roles

router = APIRouter(prefix="/visitors", tags=["visitors"])


def _ensure_status(name: str) -> VisitorStatus:
    try:
        return VisitorStatus(name)
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid visitor status '{name}'")


@router.post("/", response_model=VisitorOut, status_code=status.HTTP_201_CREATED)
def register_visitor(payload: VisitorCreate, db: Session = Depends(get_db),
                     current=Depends(get_current_user)) -> VisitorOut:
    if not current.society_id:
        raise HTTPException(status_code=400, detail="No society is linked to this account")
    privileged = current.is_superuser or bool({"admin", "committee", "security"} & set(current.role_names))
    flat_id = payload.flat_id
    if not privileged:
        if not current.resident:
            raise HTTPException(status_code=403, detail="A linked resident profile is required")
        flat_id = current.resident.flat_id
    from app.models.society import Flat
    flat = db.get(Flat, flat_id)
    if not flat or flat.society_id != current.society_id:
        raise HTTPException(status_code=400, detail="The selected flat is not in your society")
    if not is_valid_wing(flat.block.name) or not is_valid_flat(flat.number):
        raise HTTPException(status_code=400, detail="Choose a valid A-D wing and a flat from 101-104 through 401-404")
    data = payload.model_dump(exclude={"society_id", "flat_id"})
    data["expected_at"] = as_utc_naive(data.get("expected_at"))
    visitor = Visitor(
        **data,
        society_id=current.society_id,
        flat_id=flat_id,
        host_id=current.id,
        qr_code=secrets.token_urlsafe(12),
        status=VisitorStatus.pending,
    )
    db.add(visitor)
    db.flush()
    notify_roles(
        db,
        society_id=current.society_id,
        roles={"admin", "committee"},
        kind="visitor_approval_required",
        title="Visitor pass awaiting approval",
        message=f"{current.full_name} requested access for {visitor.name} to Wing {flat.block.name}, Flat {flat.number}.",
        entity_type="visitor",
        entity_id=visitor.id,
    )
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
    if current.is_superuser:
        if society_id is not None:
            q = q.where(Visitor.society_id == society_id)
    elif "security" in current.role_names or "committee" in current.role_names or "admin" in current.role_names:
        q = q.where(Visitor.society_id == current.society_id)
    elif mine:
        q = q.where(Visitor.host_id == current.id)
    else:
        q = q.where(Visitor.host_id == current.id)
    rows = db.execute(q.limit(limit)).scalars().all()
    return [VisitorOut.model_validate(v) for v in rows]


@router.patch("/{visitor_id}", response_model=VisitorOut)
def update_visitor(visitor_id: int, payload: VisitorUpdate,
                   db: Session = Depends(get_db),
                   current=Depends(get_current_user)) -> VisitorOut:
    v = db.get(Visitor, visitor_id)
    if not v:
        raise HTTPException(status_code=404, detail="Visitor not found")
    if not current.is_superuser and v.society_id != current.society_id:
        raise HTTPException(status_code=403, detail="Forbidden")
    can_manage = current.is_superuser or bool({"admin", "committee"} & set(current.role_names))
    if v.host_id != current.id and not can_manage:
        raise HTTPException(status_code=403, detail="Forbidden")
    if v.host_id == current.id and v.status != VisitorStatus.pending:
        raise HTTPException(status_code=409, detail="Only pending passes can be edited")
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
    if not current.is_superuser and v.society_id != current.society_id:
        raise HTTPException(status_code=403, detail="Forbidden")
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
        require_any_role(current, ["committee", "admin"])
        if v.status != VisitorStatus.pending:
            raise HTTPException(status_code=409, detail="Only pending passes can be approved or rejected")
    else:
        require_any_role(current, ["security", "committee", "admin"])
        expected_status = VisitorStatus.approved if action == "check_in" else VisitorStatus.checked_in
        if v.status != expected_status:
            raise HTTPException(status_code=409, detail=f"Visitor cannot {action.replace('_', ' ')} from the current status")

    v.status = mapping[action]
    db.add(VisitorLog(visitor_id=v.id, action=action, actor_id=current.id, note=payload.note))
    db.add(AuditLog(actor_id=current.id, action=f"visitor_{action}", entity_type="visitor",
                    entity_id=v.id, details=payload.note))
    if action == "approve":
        notify_roles(
            db,
            society_id=v.society_id,
            roles={"security"},
            kind="visitor_approved",
            title="Visitor approved for entry",
            message=f"{v.name} is approved for Wing {v.flat.block.name}, Flat {v.flat.number}.",
            entity_type="visitor",
            entity_id=v.id,
        )
    db.commit()
    db.refresh(v)
    return VisitorOut.model_validate(v)

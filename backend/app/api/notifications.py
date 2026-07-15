"""Authenticated in-app notification inbox."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import desc, select, update
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.core.time import utc_now
from app.db.base import get_db
from app.models.notification import UserNotification
from app.schemas.notification import NotificationOut

router = APIRouter(prefix="/notifications", tags=["notifications"])


@router.get("/", response_model=list[NotificationOut])
def list_notifications(db: Session = Depends(get_db), current=Depends(get_current_user)) -> list[NotificationOut]:
    rows = db.execute(
        select(UserNotification)
        .where(UserNotification.user_id == current.id)
        .order_by(desc(UserNotification.created_at))
        .limit(100)
    ).scalars().all()
    return [NotificationOut.model_validate(row) for row in rows]


@router.post("/{notification_id}/read", response_model=NotificationOut)
def mark_notification_read(notification_id: int, db: Session = Depends(get_db), current=Depends(get_current_user)) -> NotificationOut:
    row = db.get(UserNotification, notification_id)
    if not row or row.user_id != current.id:
        raise HTTPException(status_code=404, detail="Notification not found")
    if row.read_at is None:
        row.read_at = utc_now()
        db.commit()
        db.refresh(row)
    return NotificationOut.model_validate(row)


@router.post("/read-all")
def mark_all_notifications_read(db: Session = Depends(get_db), current=Depends(get_current_user)) -> dict:
    result = db.execute(
        update(UserNotification)
        .where(UserNotification.user_id == current.id, UserNotification.read_at.is_(None))
        .values(read_at=utc_now())
    )
    db.commit()
    return {"updated": result.rowcount or 0}

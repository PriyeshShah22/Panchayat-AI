"""Notice board router."""
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import desc, select
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, require_any_role
from app.db.base import get_db
from app.models.notice import Notice
from app.schemas.notice import NoticeCreate, NoticeOut

router = APIRouter(prefix="/notices", tags=["notices"])


@router.get("/", response_model=List[NoticeOut])
def list_notices(society_id: Optional[int] = None,
                 db: Session = Depends(get_db),
                 current=Depends(get_current_user)) -> list[NoticeOut]:
    q = select(Notice).order_by(desc(Notice.published_at))
    if society_id is not None:
        q = q.where(Notice.society_id == society_id)
    rows = db.execute(q.limit(100)).scalars().all()
    return [NoticeOut.model_validate(n) for n in rows]


@router.post("/", response_model=NoticeOut, status_code=status.HTTP_201_CREATED)
def create_notice(payload: NoticeCreate, db: Session = Depends(get_db),
                  current=Depends(get_current_user)) -> NoticeOut:
    require_any_role(current, ["admin", "committee"])
    notice = Notice(**payload.model_dump(), author_id=current.id)
    db.add(notice)
    db.commit()
    db.refresh(notice)
    return NoticeOut.model_validate(notice)


@router.delete("/{notice_id}")
def delete_notice(notice_id: int, db: Session = Depends(get_db),
                  current=Depends(get_current_user)) -> dict:
    n = db.get(Notice, notice_id)
    if not n:
        raise HTTPException(status_code=404, detail="Notice not found")
    require_any_role(current, ["admin", "committee"])
    db.delete(n)
    db.commit()
    return {"detail": "deleted"}

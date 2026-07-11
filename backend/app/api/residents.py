"""Residents router."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, require_any_role
from app.db.base import get_db
from app.models.resident import Resident
from app.models.user import User
from app.schemas.resident import ResidentCreate, ResidentOut, ResidentUpdate

router = APIRouter(prefix="/residents", tags=["residents"])


@router.get("/me", response_model=ResidentOut)
def my_profile(db: Session = Depends(get_db),
               current: User = Depends(get_current_user)) -> ResidentOut:
    resident = db.execute(select(Resident).where(Resident.user_id == current.id)).scalar_one_or_none()
    if not resident:
        raise HTTPException(status_code=404, detail="Resident profile not found")
    return ResidentOut.model_validate(resident)


@router.post("/", response_model=ResidentOut, status_code=status.HTTP_201_CREATED)
def create_resident(payload: ResidentCreate,
                    db: Session = Depends(get_db),
                    current: User = Depends(get_current_user)) -> ResidentOut:
    require_any_role(current, ["admin", "committee"])
    if db.get(Resident, payload.user_id):
        raise HTTPException(status_code=400, detail="Resident profile already exists for this user")
    resident = Resident(**payload.model_dump())
    db.add(resident)
    db.commit()
    db.refresh(resident)
    return ResidentOut.model_validate(resident)


@router.get("/", response_model=list[ResidentOut])
def list_residents(db: Session = Depends(get_db),
                   current: User = Depends(get_current_user)) -> list[ResidentOut]:
    require_any_role(current, ["admin", "committee"])
    rows = db.execute(select(Resident).limit(200)).scalars().all()
    return [ResidentOut.model_validate(r) for r in rows]


@router.patch("/{resident_id}", response_model=ResidentOut)
def update_resident(resident_id: int, payload: ResidentUpdate,
                    db: Session = Depends(get_db),
                    current: User = Depends(get_current_user)) -> ResidentOut:
    resident = db.get(Resident, resident_id)
    if not resident:
        raise HTTPException(status_code=404, detail="Resident not found")
    if resident.user_id != current.id and not current.is_superuser:
        require_any_role(current, ["admin", "committee"])
    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(resident, k, v)
    db.commit()
    db.refresh(resident)
    return ResidentOut.model_validate(resident)

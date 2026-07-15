"""Auth router: register, login, refresh, me, password change."""
from __future__ import annotations

from datetime import datetime
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from jose import JWTError
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.core.deps import get_current_user
from app.core.config import settings
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)
from app.db.base import get_db
from app.models.audit import AuditLog
from app.models.user import Role, User, UserStatus
from app.models.society import Block, Flat, Society
from app.schemas.auth import (
    LoginRequest,
    PasswordChangeRequest,
    RefreshRequest,
    RegisterRequest,
    TokenResponse,
)
from app.schemas.join_request import JoinRequestCreate, JoinRequestOut
from app.models.join_request import JoinRequest, JoinRequestStatus
from app.schemas.user import RoleOut, UserOut
from app.services.location_service import is_valid_flat, is_valid_wing


router = APIRouter(prefix="/auth", tags=["auth"])


@router.get("/societies")
def public_societies(db: Session = Depends(get_db)) -> list[dict]:
    """Minimal public directory used only to select a verified membership address."""
    societies = db.execute(select(Society).order_by(Society.name)).scalars().all()
    result = []
    for society in societies:
        blocks = db.execute(select(Block).where(
            Block.society_id == society.id,
            Block.name.in_(["A", "B", "C", "D"]),
        ).order_by(Block.name)).scalars().all()
        result.append({"id": society.id, "name": society.name, "buildings": [{
            "id": block.id, "name": block.name,
            "flats": [{"id": flat.id, "number": flat.number} for flat in db.execute(
                select(Flat).where(Flat.block_id == block.id).order_by(Flat.number)
            ).scalars().all() if is_valid_flat(flat.number)],
        } for block in blocks]})
    return result


def _build_token_response(user: User) -> TokenResponse:
    access = create_access_token(user.id, extra={"roles": user.role_names})
    refresh = create_refresh_token(user.id)
    return TokenResponse(
        access_token=access,
        refresh_token=refresh,
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        user=UserOut.model_validate(user),
    )


def _attach_default_roles(db: Session, user: User, role_names: List[str]) -> None:
    if not role_names:
        role_names = ["resident"]
    roles = db.execute(select(Role).where(Role.name.in_(role_names))).scalars().all()
    found = {r.name for r in roles}
    missing = [r for r in role_names if r not in found]
    if missing:
        # create any missing roles on-the-fly so first registration works
        for name in missing:
            role = Role(name=name, description=f"Auto-created role {name}")
            db.add(role)
        db.flush()
        roles = db.execute(select(Role).where(Role.name.in_(role_names))).scalars().all()
    user.roles = list(roles)


@router.post("/join-requests", response_model=JoinRequestOut, status_code=status.HTTP_201_CREATED)
def request_to_join(payload: JoinRequestCreate, db: Session = Depends(get_db)) -> JoinRequestOut:
    """Accept an application without creating an account or issuing credentials."""
    existing_user = db.execute(select(User).where(User.email == payload.email)).scalar_one_or_none()
    if existing_user:
        raise HTTPException(status_code=400, detail="An account already exists for this email")
    existing_request = db.execute(select(JoinRequest).where(JoinRequest.email == payload.email)).scalar_one_or_none()
    if existing_request and existing_request.status == JoinRequestStatus.pending:
        raise HTTPException(status_code=400, detail="A membership request is already waiting for review")
    if existing_request:
        db.delete(existing_request)
        db.flush()
    block = db.execute(select(Block).where(
        Block.society_id == payload.society_id,
        Block.name == payload.building_name,
    )).scalar_one_or_none()
    if not block or not is_valid_wing(block.name):
        raise HTTPException(status_code=400, detail="Select a valid building in this society")
    flat = db.execute(select(Flat).where(
        Flat.block_id == block.id,
        Flat.number == payload.flat_number,
    )).scalar_one_or_none()
    if not flat or not is_valid_flat(flat.number):
        raise HTTPException(status_code=400, detail="Select a valid flat in that building")
    request = JoinRequest(
        full_name=payload.full_name,
        email=payload.email,
        phone=payload.phone,
        date_of_birth=payload.date_of_birth,
        hashed_password=hash_password(payload.password),
        society_id=payload.society_id,
        building_name=payload.building_name.strip(),
        flat_number=payload.flat_number.strip(),
        status=JoinRequestStatus.pending,
    )
    db.add(request)
    db.commit()
    db.refresh(request)
    return JoinRequestOut.model_validate(request)


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
def register(payload: RegisterRequest, db: Session = Depends(get_db)) -> TokenResponse:
    # Keep the legacy route from silently bypassing the membership review policy.
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Accounts are created only after an administrator approves a membership request. Use /auth/join-requests.",
    )


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)) -> TokenResponse:
    user = db.execute(
        select(User).options(selectinload(User.roles)).where(User.email == payload.email)
    ).scalar_one_or_none()
    if not user or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    if user.status.value != "active" and not user.is_superuser:
        raise HTTPException(status_code=403, detail="Account not active")

    user.last_login_at = datetime.utcnow()
    db.add(AuditLog(actor_id=user.id, action="login", entity_type="user", entity_id=user.id))
    db.commit()
    db.refresh(user)
    return _build_token_response(user)


@router.post("/refresh", response_model=TokenResponse)
def refresh(payload: RefreshRequest, db: Session = Depends(get_db)) -> TokenResponse:
    try:
        data = decode_token(payload.refresh_token)
    except JWTError as exc:
        raise HTTPException(status_code=401, detail=str(exc)) from exc
    if data.get("type") != "refresh":
        raise HTTPException(status_code=401, detail="Not a refresh token")

    user = db.get(User, int(data["sub"]))
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    db.refresh(user, attribute_names=["roles"])
    return _build_token_response(user)


@router.get("/me", response_model=UserOut)
def me(current: User = Depends(get_current_user)) -> UserOut:
    return UserOut.model_validate(current)


@router.post("/password-change")
def change_password(payload: PasswordChangeRequest,
                    db: Session = Depends(get_db),
                    current: User = Depends(get_current_user)) -> dict:
    if not verify_password(payload.current_password, current.hashed_password):
        raise HTTPException(status_code=400, detail="Current password is incorrect")
    current.hashed_password = hash_password(payload.new_password)
    db.add(AuditLog(actor_id=current.id, action="password_change", entity_type="user", entity_id=current.id))
    db.commit()
    return {"detail": "Password updated"}

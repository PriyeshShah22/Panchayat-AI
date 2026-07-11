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
from app.schemas.auth import (
    LoginRequest,
    PasswordChangeRequest,
    RefreshRequest,
    RegisterRequest,
    TokenResponse,
)
from app.schemas.user import RoleOut, UserOut


router = APIRouter(prefix="/auth", tags=["auth"])


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


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
def register(payload: RegisterRequest, db: Session = Depends(get_db)) -> TokenResponse:
    existing = db.execute(select(User).where(User.email == payload.email)).scalar_one_or_none()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    user = User(
        email=payload.email,
        phone=payload.phone,
        full_name=payload.full_name,
        hashed_password=hash_password(payload.password),
        status=UserStatus.active,
        society_id=payload.society_id,
    )
    _attach_default_roles(db, user, payload.role_names)
    db.add(user)
    db.commit()
    db.refresh(user, attribute_names=["roles"])

    db.add(AuditLog(actor_id=user.id, action="register", entity_type="user", entity_id=user.id))
    db.commit()

    return _build_token_response(user)


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

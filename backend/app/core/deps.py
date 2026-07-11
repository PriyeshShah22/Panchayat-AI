"""FastAPI dependencies: current user, role guards."""
from typing import Iterable, Optional

from fastapi import Depends, Header, HTTPException, status
from jose import JWTError
from sqlalchemy.orm import Session

from app.core.security import decode_token
from app.db.base import get_db
from app.models.user import User


def get_current_user(
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db),
) -> User:
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing bearer token")
    token = authorization.split(" ", 1)[1].strip()
    try:
        payload = decode_token(token)
    except JWTError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc)) from exc

    if payload.get("type") != "access":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Wrong token type")

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token payload")

    user = db.get(User, int(user_id))
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    if user.status.value != "active" and not user.is_superuser:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Account not active")
    return user


def require_roles(*role_names: str):
    """Dependency factory: only allow callers whose roles include any of role_names."""

    allowed = set(role_names)

    def _check(current: User = Depends(get_current_user)) -> User:
        if current.is_superuser:
            return current
        if allowed.intersection(current.role_names):
            return current
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient role")

    return _check


def require_any_role(current: User, allowed: Iterable[str]) -> User:
    if current.is_superuser:
        return current
    if set(allowed).intersection(current.role_names):
        return current
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient role")

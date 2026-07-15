"""SQLAlchemy engine, session, and Base."""
from contextlib import contextmanager
from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker, Session

from app.core.config import settings


class Base(DeclarativeBase):
    """Declarative base for all ORM models."""


# SQLite needs special connect_args; Postgres works as-is.
_connect_args = {"check_same_thread": False} if settings.DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    connect_args=_connect_args,
    future=True,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, future=True)


def get_db() -> Generator[Session, None, None]:
    """FastAPI dependency that yields a database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@contextmanager
def session_scope() -> Generator[Session, None, None]:
    """Context manager equivalent of get_db for non-request callers (jobs, CLI)."""
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def create_all() -> None:
    """Create all tables from the currently imported models (used for SQLite bootstrap and tests)."""
    # Eagerly import the models package so every subclass registers on Base.metadata.
    from app.models import (  # noqa: F401
        user as _user,
        society as _society,
        resident as _resident,
        complaint as _complaint,
        visitor as _visitor,
        bill as _bill,
        notice as _notice,
        audit as _audit,
        chat as _chat,
        ai_action as _ai_action,
        join_request as _join_request,
        notification as _notification,
    )
    Base.metadata.create_all(bind=engine)

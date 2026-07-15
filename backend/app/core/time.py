"""Application time helpers.

Database timestamps stay in UTC. API consumers can therefore convert them to
the society's local timezone without inheriting the server machine timezone.
"""
from datetime import datetime, timezone


def utc_now() -> datetime:
    """Return the current UTC time as a naive value for SQLite compatibility."""
    return datetime.now(timezone.utc).replace(tzinfo=None)


def as_utc_naive(value: datetime | None) -> datetime | None:
    """Normalize an incoming aware/local datetime to naive UTC for storage."""
    if value is None:
        return None
    if value.tzinfo is None:
        return value
    return value.astimezone(timezone.utc).replace(tzinfo=None)

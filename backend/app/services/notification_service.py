"""Notifications: SMTP email + Telegram bot."""
from __future__ import annotations

import logging
import smtplib
from email.message import EmailMessage
from typing import Optional

import httpx
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.notification import UserNotification
from app.models.user import Role, User, UserStatus

logger = logging.getLogger(__name__)


def notify_roles(
    db: Session,
    *,
    society_id: int,
    roles: set[str],
    kind: str,
    title: str,
    message: str,
    entity_type: str | None = None,
    entity_id: int | None = None,
) -> int:
    """Queue an in-app notification for each matching active society user."""
    users = db.execute(
        select(User)
        .join(User.roles)
        .where(User.society_id == society_id, User.status == UserStatus.active, Role.name.in_(roles))
        .distinct()
    ).scalars().all()
    for user in users:
        db.add(UserNotification(
            society_id=society_id,
            user_id=user.id,
            kind=kind,
            title=title,
            message=message,
            entity_type=entity_type,
            entity_id=entity_id,
        ))
    return len(users)


def send_email(to: str, subject: str, html: str, text: Optional[str] = None) -> bool:
    """Send an email via SMTP. Returns True on success.

    In environments without SMTP configured this logs and returns False instead
    of raising — notifications must not break the request flow.
    """
    if not (settings.SMTP_HOST and settings.SMTP_USER and settings.SMTP_PASSWORD):
        logger.warning("SMTP not configured; would email %s subject='%s'", to, subject)
        return False

    msg = EmailMessage()
    msg["From"] = settings.SMTP_FROM or settings.SMTP_USER
    msg["To"] = to
    msg["Subject"] = subject
    msg.set_content(text or html)
    msg.add_alternative(html, subtype="html")
    try:
        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
            if settings.SMTP_USE_TLS:
                server.starttls()
            server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
            server.send_message(msg)
        return True
    except Exception as exc:
        logger.exception("SMTP send failed: %s", exc)
        return False


def send_telegram(chat_id: str, text: str) -> bool:
    """Send a Telegram message via the Bot API."""
    if not settings.TELEGRAM_BOT_TOKEN:
        logger.warning("Telegram not configured; would message %s", chat_id)
        return False
    url = f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/sendMessage"
    try:
        with httpx.Client(timeout=10) as client:
            r = client.post(url, json={"chat_id": chat_id, "text": text})
        return r.status_code == 200
    except Exception as exc:
        logger.exception("Telegram send failed: %s", exc)
        return False

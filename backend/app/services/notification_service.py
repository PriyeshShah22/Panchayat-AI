"""Notifications: SMTP email + Telegram bot."""
from __future__ import annotations

import logging
import smtplib
from email.message import EmailMessage
from typing import Optional

import httpx

from app.core.config import settings

logger = logging.getLogger(__name__)


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

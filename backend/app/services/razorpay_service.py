"""Small, auditable Razorpay Orders and signature boundary."""
import hashlib
import hmac

import httpx

from app.core.config import settings


def configured() -> bool:
    return bool(settings.RAZORPAY_KEY_ID and settings.RAZORPAY_KEY_SECRET and settings.RAZORPAY_WEBHOOK_SECRET)


def create_order(*, amount_paise: int, receipt: str, notes: dict[str, str]) -> dict:
    if not configured(): raise RuntimeError("Online UPI payment is not configured")
    response = httpx.post(f"{settings.RAZORPAY_API_BASE_URL}/orders",
        auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET), timeout=20,
        json={"amount": amount_paise, "currency": "INR", "receipt": receipt,
              "notes": notes, "payment_capture": 1})
    response.raise_for_status(); return response.json()


def verify_checkout_signature(order_id: str, payment_id: str, signature: str) -> bool:
    if not settings.RAZORPAY_KEY_SECRET: return False
    expected = hmac.new(settings.RAZORPAY_KEY_SECRET.encode(), f"{order_id}|{payment_id}".encode(), hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, signature)


def verify_webhook_signature(raw_body: bytes, signature: str) -> bool:
    if not settings.RAZORPAY_WEBHOOK_SECRET: return False
    expected = hmac.new(settings.RAZORPAY_WEBHOOK_SECRET.encode(), raw_body, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, signature)

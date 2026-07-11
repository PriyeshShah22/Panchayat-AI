"""OCR service. Google Vision in production; stub for dev/offline."""
from __future__ import annotations

import logging
from typing import Dict

import httpx

from app.core.config import settings

logger = logging.getLogger(__name__)


def ocr_extract(image_url: str, document_type: str = "auto") -> Dict:
    """Extract text from an image URL using Google Vision if configured.

    Falls back to a structured stub when OCR_PROVIDER='stub' or Vision creds
    are missing, so the rest of the system still works in development.
    """
    if settings.OCR_PROVIDER == "stub" or not settings.GOOGLE_VISION_API_KEY:
        return {
            "provider": "stub",
            "document_type": document_type,
            "fields": {
                "name": "SAMPLE NAME",
                "id_number": "XXXX-XXXX-1234",
                "issued_by": "Government of India",
            },
            "raw_text": f"[STUB OCR] document_type={document_type} image={image_url}",
        }

    try:
        # Minimal Google Vision REST call. Real systems should use google-cloud-vision.
        body = {
            "requests": [
                {
                    "image": {"source": {"imageUri": image_url}},
                    "features": [{"type": "TEXT_DETECTION"}],
                }
            ]
        }
        url = f"https://vision.googleapis.com/v1/images:annotate?key={settings.GOOGLE_VISION_API_KEY}"
        with httpx.Client(timeout=15) as client:
            r = client.post(url, json=body)
            data = r.json()
        text = (
            data.get("responses", [{}])[0].get("fullTextAnnotation", {}).get("text", "") or ""
        )
        return {"provider": "google_vision", "document_type": document_type, "raw_text": text, "fields": {}}
    except Exception as exc:
        logger.exception("Vision OCR failed: %s", exc)
        return {"provider": "google_vision_error", "document_type": document_type, "error": str(exc)}

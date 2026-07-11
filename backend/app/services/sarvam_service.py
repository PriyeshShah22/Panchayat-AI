"""Sarvam AI speech translation boundary."""
from __future__ import annotations

import httpx

from app.core.config import settings

SUPPORTED_AUDIO_TYPES = {
    "audio/wav", "audio/x-wav", "audio/mpeg", "audio/mp3", "audio/aac",
    "audio/flac", "audio/ogg", "audio/opus", "audio/webm", "video/webm",
    "audio/mp4", "video/mp4", "audio/x-m4a", "audio/amr",
}


class SarvamUnavailable(RuntimeError):
    pass


def translate_audio(audio: bytes, filename: str, content_type: str, language_code: str = "unknown") -> dict:
    if not settings.SARVAM_API_KEY:
        raise SarvamUnavailable("Sarvam speech translation is not configured.")
    if not audio:
        raise ValueError("The audio recording is empty.")
    if len(audio) > settings.MAX_UPLOAD_BYTES:
        raise ValueError("The audio recording is too large.")
    normalized_content_type = content_type.split(";", 1)[0].strip().lower()
    if normalized_content_type not in SUPPORTED_AUDIO_TYPES:
        raise ValueError("Unsupported audio format. Please record WebM, WAV, MP3, AAC, FLAC, OGG, or M4A audio.")
    try:
        with httpx.Client(timeout=35.0) as client:
            response = client.post(
                f"{settings.SARVAM_API_BASE_URL.rstrip('/')}/speech-to-text",
                headers={"api-subscription-key": settings.SARVAM_API_KEY},
                files={"file": (filename or "recording.webm", audio, normalized_content_type)},
                data={
                    "model": settings.SARVAM_STT_MODEL,
                    "mode": "translate",
                    "language_code": language_code if language_code in {"hi-IN", "mr-IN", "en-IN"} else "unknown",
                },
            )
    except httpx.RequestError as exc:
        raise SarvamUnavailable("Sarvam speech translation could not be reached.") from exc
    if response.status_code == 429:
        raise SarvamUnavailable("Sarvam is busy. Please wait a moment and try again.")
    if response.status_code >= 500:
        raise SarvamUnavailable("Sarvam speech translation is temporarily unavailable.")
    if response.status_code in {401, 403}:
        raise SarvamUnavailable("Sarvam speech translation is not authorized. Check the server configuration.")
    if response.status_code in {400, 422}:
        raise ValueError("Sarvam could not process this recording. Check the language and keep recordings under 30 seconds.")
    response.raise_for_status()
    data = response.json()
    transcript = str(data.get("transcript") or "").strip()
    if not transcript:
        raise ValueError("No clear speech was detected. Please try again.")
    return {
        "transcript": transcript,
        "language_code": data.get("language_code") or language_code,
        "language_probability": data.get("language_probability"),
        "request_id": data.get("request_id"),
    }

"""Sarvam AI speech translation boundary."""
from __future__ import annotations

import httpx

from app.core.config import settings

SUPPORTED_AUDIO_TYPES = {
    "audio/wav", "audio/x-wav", "audio/mpeg", "audio/mp3", "audio/aac",
    "audio/flac", "audio/ogg", "audio/opus", "audio/webm", "video/webm",
    "audio/mp4", "video/mp4", "audio/x-m4a", "audio/amr",
}
SUPPORTED_REPLY_LANGUAGES = {"en": "en-IN", "hi": "hi-IN", "mr": "mr-IN"}


class SarvamUnavailable(RuntimeError):
    pass


def _should_use_fallback(response: httpx.Response) -> bool:
    if response.status_code in {402, 429}:
        return True
    if response.status_code != 403:
        return False
    body = response.text.lower()
    return any(marker in body for marker in ("credit", "quota", "balance", "exhaust", "limit"))


def _source_language(data: dict | None) -> str | None:
    """Normalize both current and legacy Sarvam source-language fields."""
    if not data:
        return None
    raw = str(data.get("language_code") or data.get("source_language_code") or "").strip().lower()
    base = raw.split("-", 1)[0]
    return SUPPORTED_REPLY_LANGUAGES.get(base)


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
    requested_language = language_code if language_code in {"hi-IN", "mr-IN", "en-IN"} else "unknown"

    def request(client: httpx.Client, api_key: str, detected_language: str, mode: str = "translate") -> httpx.Response:
        return client.post(
                f"{settings.SARVAM_API_BASE_URL.rstrip('/')}/speech-to-text",
                headers={"api-subscription-key": api_key},
                files={"file": (filename or "recording.webm", audio, normalized_content_type)},
                data={
                    "model": settings.SARVAM_STT_MODEL,
                    "mode": mode,
                    "language_code": detected_language,
                },
            )

    try:
        with httpx.Client(timeout=35.0) as client:
            active_key = settings.SARVAM_API_KEY
            response = request(client, active_key, requested_language)
            if settings.SARVAM_FALLBACK_API_KEY and _should_use_fallback(response):
                active_key = settings.SARVAM_FALLBACK_API_KEY
                response = request(client, active_key, requested_language)
            if response.is_success and not str(response.json().get("transcript") or "").strip() and requested_language != "unknown":
                response = request(client, active_key, "unknown")
            detection_data = None
            if response.is_success and requested_language == "unknown" and not _source_language(response.json()):
                # Translation text is English, so it cannot reveal whether the
                # speaker used Hindi or Marathi. Ask Saaras only for the missing
                # source-language metadata while retaining the translated text.
                detection_response = request(client, active_key, "unknown", "transcribe")
                if detection_response.is_success:
                    detection_data = detection_response.json()
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
        raise ValueError("No microphone speech was detected. Check that Windows is using the correct input microphone, speak close to it for 3–10 seconds, and try again.")
    detected_language = (
        _source_language(data)
        or _source_language(detection_data)
        or _source_language({"language_code": requested_language})
        or "en-IN"
    )
    return {
        "transcript": transcript,
        "language_code": detected_language,
        "language_probability": data.get("language_probability"),
        "request_id": data.get("request_id"),
    }

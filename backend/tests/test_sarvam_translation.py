import unittest
from unittest.mock import MagicMock, patch

from app.services.sarvam_service import _source_language, translate_audio


def response(payload: dict) -> MagicMock:
    item = MagicMock()
    item.is_success = True
    item.status_code = 200
    item.json.return_value = payload
    return item


def failed_response(status_code: int, body: str) -> MagicMock:
    item = MagicMock()
    item.is_success = False
    item.status_code = status_code
    item.text = body
    return item


class SarvamTranslationTests(unittest.TestCase):
    def test_normalizes_current_and_legacy_language_fields(self):
        self.assertEqual("mr-IN", _source_language({"language_code": "mr-IN"}))
        self.assertEqual("hi-IN", _source_language({"source_language_code": "hi"}))
        self.assertIsNone(_source_language({"language_code": "unknown"}))

    @patch("app.services.sarvam_service.settings.SARVAM_API_KEY", "test-key")
    @patch("app.services.sarvam_service.httpx.Client")
    def test_preserves_detected_marathi_for_translated_audio(self, client_class):
        client = client_class.return_value.__enter__.return_value
        client.post.return_value = response(
            {"transcript": "Please show my dues.", "language_code": "mr-IN"},
        )

        result = translate_audio(b"audio", "voice.webm", "audio/webm")

        self.assertEqual("mr-IN", result["language_code"])
        self.assertEqual("translate", client.post.call_args.kwargs["data"]["mode"])
        self.assertEqual(1, client.post.call_count)

    @patch("app.services.sarvam_service.settings.SARVAM_API_KEY", "test-key")
    @patch("app.services.sarvam_service.httpx.Client")
    def test_detects_source_when_translation_omits_language(self, client_class):
        client = client_class.return_value.__enter__.return_value
        client.post.side_effect = [
            response({"transcript": "Please show my dues."}),
            response({"transcript": "माझी थकबाकी दाखवा.", "language_code": "mr-IN"}),
        ]

        result = translate_audio(b"audio", "voice.webm", "audio/webm")

        self.assertEqual("mr-IN", result["language_code"])
        self.assertEqual("transcribe", client.post.call_args.kwargs["data"]["mode"])
        self.assertEqual(2, client.post.call_count)

    @patch("app.services.sarvam_service.settings.SARVAM_FALLBACK_API_KEY", "fallback-key")
    @patch("app.services.sarvam_service.settings.SARVAM_API_KEY", "primary-key")
    @patch("app.services.sarvam_service.httpx.Client")
    def test_retries_with_fallback_when_primary_is_credit_limited(self, client_class):
        client = client_class.return_value.__enter__.return_value
        client.post.side_effect = [
            failed_response(429, "Credit limit reached"),
            response({"transcript": "Show my dues.", "language_code": "hi-IN"}),
        ]

        result = translate_audio(b"audio", "voice.webm", "audio/webm")

        self.assertEqual("hi-IN", result["language_code"])
        self.assertEqual("primary-key", client.post.call_args_list[0].kwargs["headers"]["api-subscription-key"])
        self.assertEqual("fallback-key", client.post.call_args_list[1].kwargs["headers"]["api-subscription-key"])


if __name__ == "__main__":
    unittest.main()

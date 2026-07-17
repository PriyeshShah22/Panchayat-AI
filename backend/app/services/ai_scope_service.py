"""Deterministic scope guardrails for the Panchayat AI assistant.

The language model is never used to decide whether it may widen its own scope.
Only requests related to authenticated housing-society operations are allowed
through to the model and its typed tools.
"""
from __future__ import annotations

import re
from collections.abc import Iterable


_LATIN_SCOPE_TERMS = {
    "society", "community", "building", "wing", "flat", "resident", "member",
    "committee", "chairman", "secretary", "treasurer", "admin", "panchayat",
    "maintenance", "dues", "bill", "billing", "payment", "pay", "receipt",
    "fee", "fees", "complaint", "complaints", "issue", "repair", "leak",
    "leakage", "water", "lift", "elevator", "electric", "electricity",
    "security", "parking", "garbage", "waste", "cleaning", "housekeeping",
    "notice", "announcement", "meeting", "agm", "sgm", "poll", "document",
    "noc", "visitor", "gate", "maid", "driver", "staff", "labour", "labor",
    "vendor", "contractor", "amenity", "common area", "tenant", "owner",
    "vehicle", "cheque", "check-in", "checkout", "defaulter",
    # Common Romanized Hindi and Marathi words used by the target audience.
    "society ka", "society ki", "society mein", "society me", "maintenance bharna",
    "paisa bharna", "shikayat", "takrar", "samasya", "paani", "pani", "bijli",
    "kachra", "safai", "suchna", "notice dikh", "meeting rakh", "mehmaan",
    "atithi", "chowkidar", "majdoor", "mazdoor", "rahivasi", "sabha",
}

_DEVANAGARI_SCOPE_TERMS = {
    "सोसायटी", "समाज", "इमारत", "बिल्डिंग", "विंग", "फ्लैट", "सदस्य", "रहिवासी",
    "समिति", "कमेटी", "पंचायत", "मेंटेनेंस", "रखरखाव", "बकाया", "बिल", "भुगतान",
    "पैसे", "रसीद", "शिकायत", "तक्रार", "समस्या", "मरम्मत", "पानी", "पाणी", "लिफ्ट",
    "बिजली", "वीज", "सुरक्षा", "पार्किंग", "कचरा", "सफाई", "स्वच्छता", "सूचना", "नोटिस",
    "घोषणा", "बैठक", "सभा", "दस्तावेज", "एनओसी", "मेहमान", "अतिथि", "पाहुणा", "गेट",
    "कामवाली", "ड्राइवर", "कर्मचारी", "कामगार", "मजदूर", "मजूर", "ठेकेदार", "भाडेकरू",
    "मालक", "वाहन", "चेक", "थकबाकी",
}

_OUT_OF_SCOPE_PATTERNS = (
    r"\b(?:write|make|generate|debug|fix|explain)\s+(?:me\s+)?(?:python|javascript|java|c\+\+|code|program|website|app)\b",
    r"\b(?:recipe|homework|essay|poem|story|joke|movie|celebrity|cricket score|stock|crypto|shopping|weather forecast)\b",
    r"\b(?:medical|diagnosis|medicine dosage|legal advice|investment advice)\b",
    r"\b(?:capital of|president of|prime minister of)\b",
    r"\bignore (?:all |the |your )?(?:previous |prior )?(?:rules|instructions|prompt)\b",
    r"\b(?:reveal|show|print) (?:your |the )?(?:system prompt|hidden prompt|instructions|api key|credentials)\b",
)

_GREETING_OR_HELP = {
    "hi", "hello", "hey", "namaste", "namaskar", "नमस्ते", "नमस्कार",
    "help", "help me", "what can you do", "how can you help",
    "मदद", "मदद करो", "तुम क्या कर सकते हो", "आप क्या कर सकते हैं",
    "मदत", "मदत करा", "तुम्ही काय करू शकता",
}

_CONFIRMATIONS = {
    "yes", "no", "ok", "okay", "confirm", "cancel", "proceed", "do it",
    "haan", "han", "nahi", "nahin", "हो", "होय", "नाही", "ठीक", "ठीक है",
    "करो", "करा", "रद्द", "पुष्टि",
}


def _normalize(text: str) -> str:
    return re.sub(r"\s+", " ", (text or "").casefold()).strip(" \t\r\n.!?,;:")


def _contains_latin_term(text: str, term: str) -> bool:
    return bool(re.search(rf"(?<![a-z0-9]){re.escape(term)}(?![a-z0-9])", text))


def contains_society_context(text: str) -> bool:
    """Return True when text contains an explicit society-domain concept."""
    normalized = _normalize(text)
    if any(term in normalized for term in _DEVANAGARI_SCOPE_TERMS):
        return True
    return any(_contains_latin_term(normalized, term) for term in _LATIN_SCOPE_TERMS)


def _is_explicitly_out_of_scope(text: str) -> bool:
    normalized = _normalize(text)
    return any(re.search(pattern, normalized, flags=re.IGNORECASE) for pattern in _OUT_OF_SCOPE_PATTERNS)


def _is_likely_visitor_arrival(text: str) -> bool:
    """Recognize a resident introducing an arriving guest before saying "pass".

    This is deliberately narrower than treating every mention of a friend as a
    society request: both a guest relationship and an arrival/visit expression
    must be present.
    """
    normalized = _normalize(text)
    guest_terms = (
        "friend", "guest", "relative", "visitor", "मेहमान", "दोस्त", "मित्र",
        "पाहुण", "मैत्रीण", "मित्राचा", "नातेवाईक",
    )
    arrival_terms = (
        "is coming", "will come", "coming today", "arrive", "arriving", "visit me",
        "आ रहा", "आ रही", "आएगा", "आएगी", "आने वाला", "आने वाली", "मिलने",
        "येणार", "येत आहे", "भेटायला", "भेटण्यासाठी",
    )
    return any(term in normalized for term in guest_terms) and any(
        term in normalized for term in arrival_terms
    )


def is_society_request(
    message: str,
    history: Iterable[dict] | None = None,
    *,
    has_pending_action: bool = False,
) -> bool:
    """Allow a society request, greeting, or bounded contextual follow-up.

    Explicit prompt-injection and general-purpose requests are rejected even if
    they mention the society in passing. Contextual follow-ups are allowed only
    after a recent in-scope user message, never merely because an assistant
    response happened to contain the word "society".
    """
    normalized = _normalize(message)
    if not normalized or _is_explicitly_out_of_scope(normalized):
        return False
    if normalized in _GREETING_OR_HELP:
        return True
    if contains_society_context(normalized):
        return True
    if _is_likely_visitor_arrival(normalized):
        return True

    if normalized in _CONFIRMATIONS and has_pending_action:
        return True

    recent_user_messages = [
        str(item.get("content") or "")
        for item in (history or [])
        if isinstance(item, dict) and item.get("role") == "user"
    ][-5:]
    has_recent_society_context = any(contains_society_context(item) for item in recent_user_messages)
    if not has_recent_society_context:
        return False

    # Short details and confirmations can naturally omit the subject established
    # in the previous turn. Longer topic changes must name a society concept again.
    return len(normalized.split()) <= 40


def scope_refusal(language: str) -> str:
    """Return a short, TTS-friendly refusal in the user's language."""
    code = (language or "en-IN").lower()
    if code.startswith("hi"):
        return (
            "मैं केवल आपकी सोसायटी के काम में मदद कर सकता हूँ। जैसे मेंटेनेंस, शिकायत, "
            "नोटिस, बैठक, आगंतुक, दस्तावेज और सोसायटी की सेवाएँ।"
        )
    if code.startswith("mr"):
        return (
            "मी फक्त तुमच्या सोसायटीच्या कामात मदत करू शकतो. जसे मेंटेनन्स, तक्रार, "
            "नोटीस, बैठक, पाहुणे, कागदपत्रे आणि सोसायटीच्या सेवा."
        )
    return (
        "I can only help with your society. This includes maintenance, complaints, "
        "notices, meetings, visitors, documents, and society services."
    )

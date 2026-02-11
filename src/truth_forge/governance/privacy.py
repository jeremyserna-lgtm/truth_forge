"""Lightweight privacy/PII scrubbing utilities."""

from __future__ import annotations

import re
from collections.abc import Iterable
from typing import Any


EMAIL_RE = re.compile(r"[A-Za-z0-9_.+-]+@[A-Za-z0-9-]+\.[A-Za-z0-9.-]+")
# Phone: optional +1, separators space/.-, simple groups; raw regex without escaped backslashes
PHONE_RE = re.compile(r"(?:\+?1[.\-\s]?)?(?:\(?\d{3}\)?[.\-\s]?\d{3}[.\-\s]?\d{4})")
SSN_RE = re.compile(r"\b\d{3}-\d{2}-\d{4}\b")


def scrub_text(text: str) -> str:
    """Redact common PII patterns from text."""
    scrubbed = EMAIL_RE.sub("[redacted-email]", text)
    scrubbed = PHONE_RE.sub("[redacted-phone]", scrubbed)
    scrubbed = SSN_RE.sub("[redacted-ssn]", scrubbed)
    return scrubbed


def scrub_messages(messages: Iterable[dict[str, Any]]) -> list[dict[str, Any]]:
    """Scrub PII in a list of chat messages (role/content)."""
    cleaned = []
    for msg in messages:
        if "content" in msg:
            msg = {**msg, "content": scrub_text(str(msg["content"]))}
        cleaned.append(msg)
    return cleaned

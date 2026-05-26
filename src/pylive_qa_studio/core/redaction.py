"""Redaction helpers for safe demo output and portfolio screenshots."""

from __future__ import annotations

import re

WINDOWS_PATH_RE = re.compile(r"\b[A-Za-z]:\\(?:[^\\\s:'\"]+\\)*[^\\\s:'\"]*")
UNIX_PATH_RE = re.compile(r"(?<!\w)/(?:Users|home|tmp|var|opt|workspace)/(?:[^\s:'\"]+/?)+")
TOKEN_RE = re.compile(
    r"\b(?:sk-[A-Za-z0-9_-]{12,}|gh[opsu]_[A-Za-z0-9_]{12,}|xox[baprs]-[A-Za-z0-9-]{12,})\b"
)
ENV_ASSIGNMENT_RE = re.compile(
    r"(?i)\b((?:[A-Z][A-Z0-9_]*_)?(?:API_KEY|TOKEN|SECRET|PASSWORD|PRIVATE_KEY))\s*=\s*([^\s]+)"
)


def redact_sensitive_text(text: str) -> str:
    """Remove machine-specific paths and common secret patterns from text."""

    redacted = WINDOWS_PATH_RE.sub("<local-path>", text)
    redacted = UNIX_PATH_RE.sub("<local-path>", redacted)
    redacted = TOKEN_RE.sub("<redacted-token>", redacted)
    redacted = ENV_ASSIGNMENT_RE.sub(r"\1=<redacted-secret>", redacted)
    return redacted

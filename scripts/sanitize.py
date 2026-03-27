"""Shared sanitization for untrusted GitHub metadata (repo names, descriptions).

Strips HTML tags, markdown link/image injection, and control characters
to protect against XSS in the search UI and prompt injection in LLM triage.
"""

import re

_HTML_TAG_RE = re.compile(r"<[^>]+>")
_CONTROL_CHAR_RE = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]")
_MD_LINK_RE = re.compile(r"\[([^\]]*)\]\([^)]*\)")
_MD_IMAGE_RE = re.compile(r"!\[([^\]]*)\]\([^)]*\)")
_EXCESS_WHITESPACE_RE = re.compile(r"\s{3,}")

MAX_DESCRIPTION_LEN = 500
MAX_NAME_LEN = 100


def sanitize_description(text: str) -> str:
    """Sanitize a repo/BOF description from an untrusted source."""
    if not text:
        return text
    text = _HTML_TAG_RE.sub("", text)
    text = _CONTROL_CHAR_RE.sub("", text)
    text = _MD_IMAGE_RE.sub(r"\1", text)
    text = _MD_LINK_RE.sub(r"\1", text)
    text = _EXCESS_WHITESPACE_RE.sub("  ", text)
    text = text.strip()
    if len(text) > MAX_DESCRIPTION_LEN:
        text = text[:MAX_DESCRIPTION_LEN - 1] + "\u2026"
    return text


def sanitize_name(text: str) -> str:
    """Sanitize a BOF command/tool name from an untrusted source."""
    if not text:
        return text
    text = _HTML_TAG_RE.sub("", text)
    text = _CONTROL_CHAR_RE.sub("", text)
    text = text.strip()
    if len(text) > MAX_NAME_LEN:
        text = text[:MAX_NAME_LEN - 1] + "\u2026"
    return text

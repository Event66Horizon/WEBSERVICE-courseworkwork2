"""Text normalisation and tokenisation utilities."""

from __future__ import annotations

import html
import re

TOKEN_RE = re.compile(r"[a-z0-9]+(?:'[a-z0-9]+)?", re.IGNORECASE)
WHITESPACE_RE = re.compile(r"\s+")


def normalise_text(value: str) -> str:
    """Return case-folded text with HTML entities decoded."""

    decoded = html.unescape(value)
    return WHITESPACE_RE.sub(" ", decoded.casefold()).strip()


def tokenise(value: str) -> list[str]:
    """Tokenise text into case-insensitive word tokens."""

    return TOKEN_RE.findall(normalise_text(value))


def make_snippet(text: str, query_terms: list[str], max_length: int = 180) -> str:
    """Build a compact human-readable snippet around the first query match."""

    clean = WHITESPACE_RE.sub(" ", text).strip()
    if not clean:
        return ""

    lower = clean.casefold()
    match_positions = [
        lower.find(term.casefold()) for term in query_terms if lower.find(term.casefold()) >= 0
    ]
    if not match_positions:
        return clean[:max_length]

    centre = min(match_positions)
    start = max(0, centre - max_length // 3)
    end = min(len(clean), start + max_length)
    snippet = clean[start:end].strip()
    if start > 0:
        snippet = "..." + snippet
    if end < len(clean):
        snippet += "..."
    return snippet


"""Inverted index construction and persistence."""

from __future__ import annotations

import json
import math
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from .models import Page, Posting
from .text_processing import tokenise

INDEX_VERSION = 1


@dataclass(slots=True)
class InvertedIndex:
    """A serialisable inverted index with positional word statistics."""

    postings: dict[str, dict[str, Posting]] = field(default_factory=dict)
    documents: dict[str, dict[str, Any]] = field(default_factory=dict)
    term_order: dict[str, list[str]] = field(default_factory=dict)
    document_lengths: dict[str, int] = field(default_factory=dict)

    @property
    def document_count(self) -> int:
        return len(self.documents)

    def add_page(self, page: Page) -> None:
        """Add one page to the index."""

        tokens = tokenise(page.text)
        positions: dict[str, list[int]] = defaultdict(list)
        for position, token in enumerate(tokens):
            positions[token].append(position)

        self.documents[page.url] = {
            "title": page.title,
            "text": page.text,
            "depth": page.depth,
        }
        self.term_order[page.url] = tokens
        self.document_lengths[page.url] = len(tokens)

        for term, term_positions in positions.items():
            self.postings.setdefault(term, {})[page.url] = Posting(
                url=page.url,
                frequency=len(term_positions),
                positions=tuple(term_positions),
            )

    def get_postings(self, term: str) -> list[Posting]:
        """Return postings for a normalised term."""

        normalised = tokenise(term)
        if not normalised:
            return []
        return sorted(
            self.postings.get(normalised[0], {}).values(),
            key=lambda posting: (-posting.frequency, posting.url),
        )

    def document_frequency(self, term: str) -> int:
        return len(self.postings.get(term, {}))

    def inverse_document_frequency(self, term: str) -> float:
        """Smoothed IDF to avoid division by zero."""

        return math.log((1 + self.document_count) / (1 + self.document_frequency(term))) + 1

    def to_json(self) -> dict[str, Any]:
        return {
            "version": INDEX_VERSION,
            "created_at": datetime.now(UTC).isoformat(),
            "document_count": self.document_count,
            "documents": self.documents,
            "document_lengths": self.document_lengths,
            "term_order": self.term_order,
            "postings": {
                term: {url: posting.to_json() for url, posting in url_postings.items()}
                for term, url_postings in sorted(self.postings.items())
            },
        }

    @classmethod
    def from_json(cls, payload: dict[str, Any]) -> InvertedIndex:
        version = int(payload.get("version", 0))
        if version != INDEX_VERSION:
            raise ValueError(f"Unsupported index version {version}; expected {INDEX_VERSION}.")

        return cls(
            postings={
                term: {
                    url: Posting.from_json(posting_payload)
                    for url, posting_payload in url_postings.items()
                }
                for term, url_postings in payload["postings"].items()
            },
            documents={
                url: dict(metadata) for url, metadata in payload.get("documents", {}).items()
            },
            term_order={
                url: [str(token) for token in tokens]
                for url, tokens in payload.get("term_order", {}).items()
            },
            document_lengths={
                url: int(length) for url, length in payload.get("document_lengths", {}).items()
            },
        )


def build_index(pages: list[Page]) -> InvertedIndex:
    """Build an inverted index from crawled pages."""

    index = InvertedIndex()
    for page in pages:
        index.add_page(page)
    return index


def save_index(index: InvertedIndex, path: Path) -> None:
    """Persist an index as deterministic, readable JSON."""

    path.parent.mkdir(parents=True, exist_ok=True)
    payload = index.to_json()
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def load_index(path: Path) -> InvertedIndex:
    """Load an index from disk."""

    if not path.exists():
        raise FileNotFoundError(f"Index file does not exist: {path}")
    payload = json.loads(path.read_text(encoding="utf-8"))
    return InvertedIndex.from_json(payload)


def format_postings(index: InvertedIndex, term: str) -> str:
    """Render postings for the CLI print command."""

    normalised = tokenise(term)
    if not normalised:
        return "No valid word was provided."

    target = normalised[0]
    postings = index.get_postings(target)
    if not postings:
        return f"No postings found for '{target}'."

    lines = [f"Inverted index for '{target}' ({len(postings)} page(s)):"]
    for posting in postings:
        title = index.documents.get(posting.url, {}).get("title", posting.url)
        lines.append(
            f"- {posting.url} | title={title!r} | frequency={posting.frequency} "
            f"| positions={list(posting.positions)}"
        )
    return "\n".join(lines)

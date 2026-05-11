"""Shared data models for the search engine."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True, slots=True)
class Page:
    """A crawled HTML page and its extracted searchable text."""

    url: str
    title: str
    text: str
    depth: int = 0


@dataclass(frozen=True, slots=True)
class Posting:
    """Statistics for one term in one page."""

    url: str
    frequency: int
    positions: tuple[int, ...]

    def to_json(self) -> dict[str, Any]:
        return {
            "url": self.url,
            "frequency": self.frequency,
            "positions": list(self.positions),
        }

    @classmethod
    def from_json(cls, payload: dict[str, Any]) -> Posting:
        return cls(
            url=str(payload["url"]),
            frequency=int(payload["frequency"]),
            positions=tuple(int(position) for position in payload["positions"]),
        )


@dataclass(frozen=True, slots=True)
class SearchResult:
    """A ranked search result for a query."""

    url: str
    title: str
    score: float
    matched_terms: tuple[str, ...]
    snippet: str

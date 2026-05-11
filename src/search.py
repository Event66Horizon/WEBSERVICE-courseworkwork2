"""Query processing and ranked retrieval."""

from __future__ import annotations

from collections import Counter

from .indexer import InvertedIndex
from .models import SearchResult
from .text_processing import make_snippet, tokenise


class SearchEngine:
    """Search interface over an :class:`InvertedIndex`."""

    def __init__(self, index: InvertedIndex) -> None:
        self.index = index

    def find(self, query: str, limit: int | None = None) -> list[SearchResult]:
        """Find pages containing all query terms, preferring exact phrase matches."""

        terms = tokenise(query)
        if not terms:
            return []

        candidate_urls = self._candidate_urls(terms)
        results: list[SearchResult] = []
        query_counts = Counter(terms)

        for url in candidate_urls:
            tokens = self.index.term_order.get(url, [])
            phrase_match = self._contains_phrase(tokens, terms)
            score = self._tf_idf_score(url, query_counts)
            if phrase_match:
                score *= 2.0

            metadata = self.index.documents.get(url, {})
            results.append(
                SearchResult(
                    url=url,
                    title=str(metadata.get("title", url)),
                    score=score,
                    matched_terms=tuple(terms),
                    snippet=make_snippet(str(metadata.get("text", "")), terms),
                )
            )

        results.sort(key=lambda result: (-result.score, result.url))
        return results if limit is None else results[:limit]

    def _candidate_urls(self, terms: list[str]) -> set[str]:
        posting_sets = [
            set(self.index.postings.get(term, {}).keys())
            for term in terms
        ]
        if not posting_sets:
            return set()
        return set.intersection(*posting_sets)

    def _tf_idf_score(self, url: str, query_counts: Counter[str]) -> float:
        doc_length = max(self.index.document_lengths.get(url, 0), 1)
        score = 0.0
        for term, query_frequency in query_counts.items():
            posting = self.index.postings.get(term, {}).get(url)
            if posting is None:
                continue
            term_frequency = posting.frequency / doc_length
            score += query_frequency * term_frequency * self.index.inverse_document_frequency(term)
        return score

    @staticmethod
    def _contains_phrase(tokens: list[str], terms: list[str]) -> bool:
        if len(terms) == 1:
            return terms[0] in tokens
        if len(tokens) < len(terms):
            return False
        phrase_length = len(terms)
        return any(
            tokens[start : start + phrase_length] == terms
            for start in range(0, len(tokens) - phrase_length + 1)
        )


def format_results(results: list[SearchResult], query: str) -> str:
    """Render search results for the CLI find command."""

    if not tokenise(query):
        return "Please enter a non-empty search query."
    if not results:
        return f"No pages found for query: {query!r}"

    lines = [f"Found {len(results)} page(s) for {query!r}:"]
    for rank, result in enumerate(results, start=1):
        lines.append(
            f"{rank}. {result.url} | score={result.score:.4f} | title={result.title!r}"
        )
        if result.snippet:
            lines.append(f"   {result.snippet}")
    return "\n".join(lines)


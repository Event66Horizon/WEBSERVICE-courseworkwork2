from __future__ import annotations

from pathlib import Path

from src.indexer import build_index, format_postings, load_index, save_index
from src.models import Page


def test_build_index_records_frequency_and_positions() -> None:
    index = build_index(
        [
            Page(
                url="https://quotes.toscrape.com/",
                title="Quotes",
                text="Good friends are good company.",
            )
        ]
    )

    postings = index.get_postings("GOOD")

    assert len(postings) == 1
    assert postings[0].frequency == 2
    assert postings[0].positions == (0, 3)


def test_index_round_trip_preserves_documents_and_postings(tmp_path: Path) -> None:
    path = tmp_path / "index.json"
    index = build_index([Page(url="u1", title="T1", text="alpha beta alpha")])

    save_index(index, path)
    loaded = load_index(path)

    assert loaded.document_count == 1
    assert loaded.documents["u1"]["title"] == "T1"
    assert loaded.get_postings("alpha")[0].frequency == 2


def test_format_postings_handles_missing_word() -> None:
    index = build_index([Page(url="u1", title="T1", text="alpha beta")])

    assert "No postings found" in format_postings(index, "missing")


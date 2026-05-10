from src.indexer import build_index
from src.models import Page
from src.search import SearchEngine, format_results


def make_engine() -> SearchEngine:
    index = build_index(
        [
            Page(
                url="u1",
                title="Phrase hit",
                text="Good friends, good books, and a sleepy conscience.",
            ),
            Page(
                url="u2",
                title="Separated terms",
                text="Good habits matter. Old friends matter too.",
            ),
            Page(url="u3", title="No match", text="Tenderness of heart."),
        ]
    )
    return SearchEngine(index)


def test_find_supports_multi_word_queries_and_boosts_exact_phrase() -> None:
    results = make_engine().find("good friends")

    assert [result.url for result in results] == ["u1", "u2"]
    assert results[0].score > results[1].score


def test_find_returns_empty_for_empty_or_missing_queries() -> None:
    engine = make_engine()

    assert engine.find("") == []
    assert engine.find("notpresent") == []


def test_format_results_reports_empty_query_and_missing_results() -> None:
    assert "non-empty" in format_results([], "")
    assert "No pages found" in format_results([], "notpresent")


from src.text_processing import make_snippet, tokenise


def test_tokenise_is_case_insensitive_and_handles_apostrophes() -> None:
    assert tokenise("Good FRIENDS aren't rare.") == ["good", "friends", "aren't", "rare"]


def test_make_snippet_prefers_query_location() -> None:
    snippet = make_snippet("alpha beta gamma delta epsilon", ["gamma"], max_length=18)

    assert "gamma" in snippet


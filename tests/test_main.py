from __future__ import annotations

from pathlib import Path
from typing import Any

from src import main
from src.indexer import build_index
from src.models import Page


class FakeCrawler:
    def __init__(self, config: object) -> None:
        self.config = config

    def crawl(self) -> list[Page]:
        return [
            Page(
                url="https://quotes.toscrape.com/",
                title="Quotes",
                text="Good friends and good books.",
            )
        ]


def make_shell(tmp_path: Path) -> main.SearchShell:
    return main.SearchShell(
        index_path=tmp_path / "index.json",
        start_url="https://quotes.toscrape.com/",
        politeness_window=6.0,
    )


def test_shell_requires_index_before_print_or_find(tmp_path: Path, capsys: Any) -> None:
    shell = make_shell(tmp_path)

    shell.do_print("good")
    shell.do_find("good")
    output = capsys.readouterr().out

    assert output.count("No index is loaded") == 2


def test_shell_build_load_print_and_find(
    tmp_path: Path,
    capsys: Any,
    monkeypatch: Any,
) -> None:
    monkeypatch.setattr(main, "Crawler", FakeCrawler)
    shell = make_shell(tmp_path)

    shell.do_build("")
    shell.do_load("")
    shell.do_print("good")
    shell.do_find("good friends")
    output = capsys.readouterr().out

    assert "Built index for 1 page" in output
    assert "Loaded index for 1 page" in output
    assert "Inverted index for 'good'" in output
    assert "Found 1 page(s)" in output
    assert shell.index_path.exists()


def test_shell_reports_invalid_command_usage(tmp_path: Path, capsys: Any) -> None:
    shell = make_shell(tmp_path)

    shell.do_build("unexpected")
    shell.do_load("unexpected")
    shell.index = build_index([Page(url="u1", title="T1", text="alpha beta")])
    shell.do_print("too many words")
    shell.default("unknown")
    shell.emptyline()
    output = capsys.readouterr().out

    assert "build command does not take arguments" in output
    assert "load command does not take arguments" in output
    assert "Usage: print <word>" in output
    assert "Unknown command" in output


def test_shell_reports_missing_index_file(tmp_path: Path, capsys: Any) -> None:
    shell = make_shell(tmp_path)

    shell.do_load("")
    output = capsys.readouterr().out

    assert "Could not load index" in output


def test_shell_exit_commands_return_true(tmp_path: Path) -> None:
    shell = make_shell(tmp_path)

    assert shell.do_exit("") is True
    assert shell.do_quit("") is True


def test_parse_args_and_main_start_shell(monkeypatch: Any) -> None:
    started: list[tuple[Path, str, float]] = []

    class FakeShell:
        def __init__(self, index_path: Path, start_url: str, politeness_window: float) -> None:
            started.append((index_path, start_url, politeness_window))

        def cmdloop(self) -> None:
            return None

    monkeypatch.setattr(
        "sys.argv",
        [
            "prog",
            "--index",
            "data/custom.json",
            "--start-url",
            "https://quotes.toscrape.com/",
            "--politeness-window",
            "6",
            "--log-level",
            "INFO",
        ],
    )
    monkeypatch.setattr(main, "SearchShell", FakeShell)

    main.main()

    assert started == [(Path("data/custom.json"), "https://quotes.toscrape.com/", 6.0)]

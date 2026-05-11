"""Command-line shell for the coursework search engine."""

from __future__ import annotations

import argparse
import cmd
import logging
from pathlib import Path

from .crawler import CrawlConfig, Crawler
from .indexer import InvertedIndex, build_index, format_postings, load_index, save_index
from .search import SearchEngine, format_results

DEFAULT_INDEX_PATH = Path("data/index.json")


class SearchShell(cmd.Cmd):
    """Interactive shell implementing build, load, print and find."""

    intro = "XJCO3011 Search Tool. Type help or ? to list commands."
    prompt = "search> "

    def __init__(self, index_path: Path, start_url: str, politeness_window: float) -> None:
        super().__init__()
        self.index_path = index_path
        self.start_url = start_url
        self.politeness_window = politeness_window
        self.index: InvertedIndex | None = None

    def do_build(self, arg: str) -> None:
        """build: crawl the target website, build the index, and save it."""

        if arg.strip():
            print("The build command does not take arguments.")
            return
        config = CrawlConfig(
            start_url=self.start_url,
            politeness_window=self.politeness_window,
        )
        print(f"Crawling {config.start_url} with {config.politeness_window:.0f}s politeness...")
        pages = Crawler(config).crawl()
        self.index = build_index(pages)
        save_index(self.index, self.index_path)
        print(
            f"Built index for {self.index.document_count} page(s), "
            f"{len(self.index.postings)} unique term(s). Saved to {self.index_path}."
        )

    def do_load(self, arg: str) -> None:
        """load: load the index from the file system."""

        if arg.strip():
            print("The load command does not take arguments.")
            return
        try:
            self.index = load_index(self.index_path)
        except (FileNotFoundError, ValueError) as exc:
            print(f"Could not load index: {exc}")
            return
        print(
            f"Loaded index for {self.index.document_count} page(s), "
            f"{len(self.index.postings)} unique term(s)."
        )

    def do_print(self, arg: str) -> None:
        """print <word>: print the inverted index for one word."""

        if self.index is None:
            print("No index is loaded. Run build or load first.")
            return
        if len(arg.split()) != 1:
            print("Usage: print <word>")
            return
        print(format_postings(self.index, arg))

    def do_find(self, arg: str) -> None:
        """find <query>: return ranked pages containing the query terms."""

        if self.index is None:
            print("No index is loaded. Run build or load first.")
            return
        print(format_results(SearchEngine(self.index).find(arg), arg))

    def do_exit(self, arg: str) -> bool:
        """exit: leave the shell."""

        return True

    def do_quit(self, arg: str) -> bool:
        """quit: leave the shell."""

        return True

    def emptyline(self) -> bool:
        """Ignore empty input rather than repeating the previous command."""
        return False

    def default(self, line: str) -> None:
        print(f"Unknown command: {line}. Type help or ? for available commands.")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="XJCO3011 coursework search engine tool")
    parser.add_argument("--index", type=Path, default=DEFAULT_INDEX_PATH, help="Index JSON path")
    parser.add_argument(
        "--start-url",
        default="https://quotes.toscrape.com/",
        help="Crawler start URL",
    )
    parser.add_argument(
        "--politeness-window",
        type=float,
        default=6.0,
        help="Seconds between successive HTTP requests; must be at least 6",
    )
    parser.add_argument(
        "--log-level",
        default="WARNING",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    logging.basicConfig(level=getattr(logging, args.log_level))
    SearchShell(
        index_path=args.index,
        start_url=args.start_url,
        politeness_window=args.politeness_window,
    ).cmdloop()


if __name__ == "__main__":
    main()

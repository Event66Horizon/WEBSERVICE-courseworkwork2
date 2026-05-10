from __future__ import annotations

from pathlib import Path

from src.crawler import CrawlConfig, Crawler


class FakeResponse:
    def __init__(self, url: str, text: str, status_code: int = 200) -> None:
        self.url = url
        self.text = text
        self.status_code = status_code

    def raise_for_status(self) -> None:
        if self.status_code >= 400:
            raise RuntimeError(f"HTTP {self.status_code}")


def read_fixture(name: str) -> str:
    return (Path(__file__).parent / "fixtures" / name).read_text(encoding="utf-8")


def test_crawler_fetches_reachable_in_domain_pages_and_extracts_quote_text() -> None:
    pages = {
        "https://quotes.toscrape.com/": read_fixture("page1.html"),
        "https://quotes.toscrape.com/page/2/": read_fixture("page2.html"),
        "https://quotes.toscrape.com/tag/change/page/1/": read_fixture("page2.html"),
        "https://quotes.toscrape.com/tag/friends/page/1/": read_fixture("page2.html"),
    }
    calls: list[str] = []
    sleeps: list[float] = []

    def fetch(url: str) -> FakeResponse:
        calls.append(url)
        return FakeResponse(url=url, text=pages[url])

    def record_sleep(seconds: float) -> None:
        sleeps.append(seconds)

    crawler = Crawler(
        CrawlConfig(max_pages=2),
        fetch=fetch,
        sleep=record_sleep,
    )

    result = crawler.crawl()

    assert [page.url for page in result] == [
        "https://quotes.toscrape.com/",
        "https://quotes.toscrape.com/tag/change/page/1/",
    ]
    assert calls == [page.url for page in result]
    assert len(sleeps) == 1
    assert sleeps[0] >= 5.9
    assert "Good friends" in result[0].text


def test_crawl_config_rejects_short_politeness_window() -> None:
    try:
        CrawlConfig(politeness_window=1.0)
    except ValueError as exc:
        assert "at least 6 seconds" in str(exc)
    else:
        raise AssertionError("Expected ValueError for too-small politeness window")

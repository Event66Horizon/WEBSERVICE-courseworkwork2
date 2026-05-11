"""Polite crawler for https://quotes.toscrape.com/."""

from __future__ import annotations

import logging
import time
from collections import deque
from collections.abc import Callable, Iterable
from dataclasses import dataclass
from typing import Protocol
from urllib.parse import urldefrag, urljoin, urlparse

import requests
from bs4 import BeautifulSoup

from .models import Page

LOGGER = logging.getLogger(__name__)
DEFAULT_START_URL = "https://quotes.toscrape.com/"


class HttpResponse(Protocol):
    """Small response protocol, making the crawler easy to mock in tests."""

    text: str
    url: str
    status_code: int

    def raise_for_status(self) -> None:
        """Raise an exception for HTTP errors."""


FetchFunction = Callable[[str], HttpResponse]
SleepFunction = Callable[[float], None]


@dataclass(frozen=True, slots=True)
class CrawlConfig:
    """Crawler configuration."""

    start_url: str = DEFAULT_START_URL
    politeness_window: float = 6.0
    timeout: float = 15.0
    max_pages: int | None = None
    user_agent: str = "XJCO3011-SearchTool/1.0 (+coursework crawler)"

    def __post_init__(self) -> None:
        if self.politeness_window < 6.0:
            raise ValueError("The politeness window must be at least 6 seconds.")
        if self.timeout <= 0:
            raise ValueError("Timeout must be positive.")
        if self.max_pages is not None and self.max_pages <= 0:
            raise ValueError("max_pages must be positive when provided.")


class Crawler:
    """Breadth-first crawler constrained to the target website."""

    def __init__(
        self,
        config: CrawlConfig | None = None,
        fetch: FetchFunction | None = None,
        sleep: SleepFunction = time.sleep,
    ) -> None:
        self.config = config or CrawlConfig()
        self._session = requests.Session()
        self._session.headers.update({"User-Agent": self.config.user_agent})
        self._fetch = fetch or self._default_fetch
        self._sleep = sleep
        self._last_request_at: float | None = None
        self._allowed_netloc = urlparse(self.config.start_url).netloc

    def crawl(self) -> list[Page]:
        """Crawl all reachable in-domain pages from the configured start URL."""

        queue: deque[tuple[str, int]] = deque([(self._canonicalise(self.config.start_url), 0)])
        seen: set[str] = set()
        pages: list[Page] = []

        while queue:
            url, depth = queue.popleft()
            if url in seen:
                continue
            if self.config.max_pages is not None and len(pages) >= self.config.max_pages:
                break

            seen.add(url)
            try:
                html = self._fetch_html(url)
            except requests.RequestException as exc:
                LOGGER.warning("Skipping %s after request failure: %s", url, exc)
                continue

            page = self._parse_page(url, html, depth)
            pages.append(page)

            for link in self._extract_links(url, html):
                if link not in seen:
                    queue.append((link, depth + 1))

        return pages

    def _default_fetch(self, url: str) -> requests.Response:
        return self._session.get(url, timeout=self.config.timeout)

    def _fetch_html(self, url: str) -> str:
        self._respect_politeness_window()
        response = self._fetch(url)
        response.raise_for_status()
        return response.text

    def _respect_politeness_window(self) -> None:
        now = time.monotonic()
        if self._last_request_at is not None:
            elapsed = now - self._last_request_at
            remaining = self.config.politeness_window - elapsed
            if remaining > 0:
                self._sleep(remaining)
        self._last_request_at = time.monotonic()

    def _extract_links(self, base_url: str, html: str) -> Iterable[str]:
        soup = BeautifulSoup(html, "html.parser")
        for anchor in soup.find_all("a", href=True):
            href = anchor.get("href")
            if not isinstance(href, str):
                continue
            canonical = self._canonicalise(urljoin(base_url, href))
            if self._is_allowed(canonical):
                yield canonical

    def _parse_page(self, url: str, html: str, depth: int) -> Page:
        soup = BeautifulSoup(html, "html.parser")
        for element in soup(["script", "style", "noscript"]):
            element.decompose()

        title = soup.title.get_text(" ", strip=True) if soup.title else url
        quotes = [quote.get_text(" ", strip=True) for quote in soup.select(".quote")]
        body_text = " ".join(quotes) if quotes else soup.get_text(" ", strip=True)
        return Page(url=url, title=title, text=body_text, depth=depth)

    def _canonicalise(self, url: str) -> str:
        clean, _fragment = urldefrag(url)
        parsed = urlparse(clean)
        path = parsed.path or "/"
        canonical = parsed._replace(path=path, query="", fragment="").geturl()
        return canonical

    def _is_allowed(self, url: str) -> bool:
        parsed = urlparse(url)
        return parsed.scheme in {"http", "https"} and parsed.netloc == self._allowed_netloc

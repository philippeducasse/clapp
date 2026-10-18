"""Fetch a web page politely and turn it into text.

- `httpx` with a timeout, a few redirects and a page-size cap (larger pages are truncated).
- Respects `robots.txt` (RFC 9309: a 4xx robots.txt allows everything, 401/403, 5xx or an
  unreachable server disallow everything).
- At most one request per second per domain (`PER_DOMAIN_INTERVAL_SECONDS`).
- Pages are cached for 30 days in `diskcache` (`CACHE_DIR`, a Docker volume in production), so
  re-running a discovery doesn't hit the same sites again.
- The main text comes from `trafilatura`. Pages with no readable text (usually JavaScript-only
  sites) come back with `is_empty=True` and are logged as "empty content"; callers skip them.
"""

import asyncio
import logging
import re
import time
from typing import Any
from urllib.parse import urldefrag, urlsplit
from urllib.robotparser import RobotFileParser

import diskcache
import httpx
import lxml.html
import trafilatura
from lxml import etree
from pydantic import BaseModel

from discovery.config import Settings
from discovery.llm import RunBudget
from discovery.tools.domains import domain_of

logger = logging.getLogger(__name__)

ROBOTS_AGENT = "clapp-discovery"
ROBOTS_TTL_SECONDS = 24 * 3600
# Below this many characters of readable text, a page counts as empty (JavaScript-only, splash).
MIN_TEXT_CHARS = 80
HTML_TYPES = ("text/html", "application/xhtml+xml", "text/plain")

_META_CHARSET = re.compile(rb"""<meta[^>]+charset=["']?([\w-]+)""", re.IGNORECASE)
_TITLE = re.compile(r"<title[^>]*>(.*?)</title>", re.IGNORECASE | re.DOTALL)


class FetchError(Exception):
    """The page couldn't be fetched. `reason` is one of: invalid_url, robots, network,
    http_status, not_html."""

    def __init__(self, url: str, reason: str, detail: str = ""):
        super().__init__(f"{url}: {reason}{f' ({detail})' if detail else ''}")
        self.url = url
        self.reason = reason
        self.detail = detail


class Page(BaseModel):
    url: str  # as requested (without #fragment)
    final_url: str  # after redirects
    status: int
    title: str = ""
    html: str = ""
    text: str = ""  # main readable text
    truncated: bool = False
    from_cache: bool = False

    @property
    def is_empty(self) -> bool:
        return len(self.text.strip()) < MIN_TEXT_CHARS


def clean_url(url: str) -> str:
    """Strip whitespace and the #fragment. Raises FetchError for anything but http(s)."""
    url = urldefrag((url or "").strip())[0]
    parts = urlsplit(url)
    if parts.scheme not in ("http", "https") or not parts.hostname:
        raise FetchError(url, "invalid_url")
    return url


class Fetcher:
    def __init__(
        self,
        settings: Settings,
        transport: httpx.AsyncBaseTransport | None = None,
        cache: diskcache.Cache | None = None,
    ):
        self.settings = settings
        self._client = httpx.AsyncClient(
            transport=transport,
            timeout=settings.fetch_timeout_seconds,
            follow_redirects=True,
            max_redirects=5,
            headers={
                "User-Agent": settings.user_agent,
                "Accept": "text/html,application/xhtml+xml;q=0.9,text/plain;q=0.5,*/*;q=0.1",
                "Accept-Language": "en,fr;q=0.9,de;q=0.8,nl;q=0.7,es;q=0.6,it;q=0.6,*;q=0.5",
            },
        )
        self._cache = cache if cache is not None else diskcache.Cache(settings.cache_dir)
        self._owns_cache = cache is None
        self._robots: dict[str, RobotFileParser] = {}
        self._domain_locks: dict[str, asyncio.Lock] = {}
        self._next_request_at: dict[str, float] = {}

    async def aclose(self) -> None:
        await self._client.aclose()
        if self._owns_cache:
            self._cache.close()

    async def fetch(self, url: str, budget: RunBudget | None = None) -> Page:
        """Fetch `url` (or read it from the cache). Counts one page against `budget`.

        Raises FetchError when the page can't be used, BudgetExceeded when the page budget is
        spent.
        """
        url = clean_url(url)
        if budget is not None:
            budget.spend("pages")

        cached = self._cache_get(f"page:{url}")
        if cached is not None:
            page = Page.model_validate({**cached, "from_cache": True})
            if page.is_empty:
                logger.info("Empty content (cached): %s", url)
            return page

        if not await self._allowed_by_robots(url):
            raise FetchError(url, "robots", "disallowed by robots.txt")

        status, final_url, content_type, body, truncated = await self._get(url)
        if status >= 400:
            raise FetchError(url, "http_status", str(status))
        if content_type and not content_type.startswith(HTML_TYPES):
            raise FetchError(url, "not_html", content_type)

        html = _decode(body, content_type)
        text, title = await asyncio.to_thread(_extract, html, final_url)
        page = Page(
            url=url,
            final_url=final_url,
            status=status,
            title=title,
            html=html,
            text=text,
            truncated=truncated,
        )
        if page.is_empty:
            logger.info("Empty content (probably JavaScript-only): %s", url)
        self._cache_set(f"page:{url}", page.model_dump(exclude={"from_cache"}))
        return page

    # --- HTTP ---------------------------------------------------------------------------------

    async def _get(self, url: str) -> tuple[int, str, str, bytes, bool]:
        """GET with the per-domain rate limit and the size cap."""
        await self._wait_turn(domain_of(url))
        limit = self.settings.max_page_bytes
        try:
            async with self._client.stream("GET", url) as response:
                chunks: list[bytes] = []
                size = 0
                truncated = False
                async for chunk in response.aiter_bytes():
                    chunks.append(chunk)
                    size += len(chunk)
                    if size >= limit:
                        truncated = True
                        break
                content_type = response.headers.get("content-type", "").lower()
                return (
                    response.status_code,
                    str(response.url),
                    content_type,
                    b"".join(chunks)[:limit],
                    truncated,
                )
        except httpx.HTTPError as exc:
            raise FetchError(url, "network", repr(exc)) from exc

    async def _wait_turn(self, domain: str) -> None:
        """Space out requests to the same domain by PER_DOMAIN_INTERVAL_SECONDS."""
        interval = self.settings.per_domain_interval_seconds
        lock = self._domain_locks.setdefault(domain, asyncio.Lock())
        async with lock:
            wait = self._next_request_at.get(domain, 0.0) - time.monotonic()
            if wait > 0:
                await asyncio.sleep(wait)
            self._next_request_at[domain] = time.monotonic() + interval

    # --- robots.txt ---------------------------------------------------------------------------

    async def _allowed_by_robots(self, url: str) -> bool:
        parts = urlsplit(url)
        origin = f"{parts.scheme}://{parts.netloc}"
        parser = self._robots.get(origin)
        if parser is None:
            parser = await self._load_robots(origin)
            self._robots[origin] = parser
        return parser.can_fetch(ROBOTS_AGENT, url)

    async def _load_robots(self, origin: str) -> RobotFileParser:
        parser = RobotFileParser()
        key = f"robots:{origin}"
        cached = self._cache_get(key)
        if cached is None:
            cached = await self._fetch_robots(origin)
            self._cache_set(key, cached, ttl=ROBOTS_TTL_SECONDS)
        if cached["rule"] == "allow_all":
            parser.allow_all = True
        elif cached["rule"] == "disallow_all":
            parser.disallow_all = True
        else:
            parser.parse(cached["body"].splitlines())
        # RobotFileParser.can_fetch answers False until it thinks robots.txt was read.
        parser.modified()
        return parser

    async def _fetch_robots(self, origin: str) -> dict[str, Any]:
        try:
            status, _, _, body, _ = await self._get(f"{origin}/robots.txt")
        except FetchError as exc:
            logger.info("robots.txt unreachable for %s (%s): not fetching", origin, exc.detail)
            return {"rule": "disallow_all"}
        if status in (401, 403) or status >= 500:
            return {"rule": "disallow_all"}
        if status >= 400:
            return {"rule": "allow_all"}
        return {"rule": "parse", "body": body.decode("utf-8", errors="replace")}

    # --- cache --------------------------------------------------------------------------------

    def _cache_get(self, key: str) -> Any:
        if self.settings.cache_ttl_days <= 0:
            return None
        return self._cache.get(key)

    def _cache_set(self, key: str, value: Any, ttl: float | None = None) -> None:
        if self.settings.cache_ttl_days <= 0:
            return
        self._cache.set(key, value, expire=ttl or self.settings.cache_ttl_days * 24 * 3600)


def _decode(body: bytes, content_type: str) -> str:
    """Charset from the Content-Type header, then <meta charset>, then UTF-8, then cp1252."""
    candidates: list[str] = []
    if "charset=" in content_type:
        candidates.append(content_type.split("charset=", 1)[1].split(";")[0].strip(" \"'"))
    if match := _META_CHARSET.search(body[:4096]):
        candidates.append(match.group(1).decode("ascii", errors="ignore"))
    for encoding in [*candidates, "utf-8"]:
        try:
            return body.decode(encoding)
        except (LookupError, UnicodeDecodeError):
            continue
    return body.decode("cp1252", errors="replace")


def _extract(html: str, url: str) -> tuple[str, str]:
    """(main text, title). Falls back to the whole visible text when trafilatura finds nothing,
    so short listing pages (calendars, contact pages) aren't lost."""
    title = ""
    if match := _TITLE.search(html[:20000]):
        title = " ".join(match.group(1).split())[:300]
    if not html.strip():
        return "", title
    text = (
        # get main text from the page, excluding headers, navigation, footers, etc. input: raw HTML, output: text.
        # client side rendered pages will show nothing here.
        trafilatura.extract(
            html,
            url=url,
            favor_recall=True,
            include_comments=False,
            include_tables=True,
            deduplicate=False,
        )
        or ""
    )
    if len(text.strip()) < MIN_TEXT_CHARS:
        text = _visible_text(html) or text
    return text.strip(), title


def _visible_text(html: str) -> str:
    try:
        tree = lxml.html.fromstring(html)
    except (etree.ParserError, ValueError):
        return ""
    for element in tree.xpath("//script|//style|//noscript|//template"):
        element.drop_tree()
    lines = (" ".join(line.split()) for line in tree.text_content().splitlines())
    return "\n".join(line for line in lines if line)

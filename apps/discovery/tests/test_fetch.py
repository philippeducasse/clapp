import time

import diskcache
import httpx
import pytest
import respx

from discovery.config import Settings
from discovery.llm import BudgetExceeded, RunBudget
from discovery.tools.fetch import Fetcher, FetchError, clean_url
from tests.conftest import fixture_bytes

SITE = "https://lesjongleurs.fr"
HTML = {"content-type": "text/html; charset=utf-8"}


@pytest.fixture
def settings(tmp_path) -> Settings:
    return Settings(
        _env_file=None,
        cache_dir=str(tmp_path / "cache"),
        per_domain_interval_seconds=0,
        max_page_bytes=1_000_000,
    )


@pytest.fixture
def web():
    with respx.mock(assert_all_called=False) as router:
        router.get(f"{SITE}/robots.txt").respond(200, text="User-agent: *\nDisallow: /private/\n")
        router.get(f"{SITE}/").respond(200, content=fixture_bytes("artist_home.html"), headers=HTML)
        router.get(f"{SITE}/agenda/").respond(
            200, content=fixture_bytes("calendar.html"), headers=HTML
        )
        yield router


@pytest.fixture
async def fetcher(settings):
    cache = diskcache.Cache(settings.cache_dir)
    fetcher = Fetcher(settings, cache=cache)
    yield fetcher
    await fetcher.aclose()
    cache.close()


async def test_fetch_returns_title_html_and_main_text(web, fetcher):
    page = await fetcher.fetch(f"{SITE}/agenda/#2026")

    assert page.url == f"{SITE}/agenda/"
    assert page.final_url == f"{SITE}/agenda/"
    assert page.status == 200
    assert page.title == "Agenda — Compagnie Les Jongleurs"
    assert "Chalon dans la Rue" in page.text
    assert 'href="https://chalondanslarue.com/"' in page.html
    assert not page.is_empty
    assert not page.from_cache


async def test_second_fetch_comes_from_the_cache(web, fetcher):
    await fetcher.fetch(f"{SITE}/agenda/")
    calls_before = len(web.calls)

    page = await fetcher.fetch(f"{SITE}/agenda/")

    assert page.from_cache
    assert "Chalon dans la Rue" in page.text
    assert len(web.calls) == calls_before


async def test_cache_survives_a_new_fetcher(web, settings):
    with diskcache.Cache(settings.cache_dir) as cache:
        first = Fetcher(settings, cache=cache)
        await first.fetch(f"{SITE}/agenda/")
        await first.aclose()
        calls = len(web.calls)

        second = Fetcher(settings, cache=cache)
        page = await second.fetch(f"{SITE}/agenda/")
        await second.aclose()

    assert page.from_cache
    assert len(web.calls) == calls


async def test_no_cache_when_ttl_is_zero(web, tmp_path):
    settings = Settings(
        _env_file=None, cache_dir=str(tmp_path), cache_ttl_days=0, per_domain_interval_seconds=0
    )
    fetcher = Fetcher(settings)
    await fetcher.fetch(f"{SITE}/agenda/")
    page = await fetcher.fetch(f"{SITE}/agenda/")
    await fetcher.aclose()
    assert not page.from_cache


async def test_robots_txt_is_fetched_once_and_respected(web, fetcher):
    private = web.get(f"{SITE}/private/x").respond(200, text="secret", headers=HTML)

    with pytest.raises(FetchError) as exc:
        await fetcher.fetch(f"{SITE}/private/x")
    assert exc.value.reason == "robots"
    assert not private.called

    await fetcher.fetch(f"{SITE}/")
    await fetcher.fetch(f"{SITE}/agenda/")
    assert web.routes[0].call_count == 1  # robots.txt


@pytest.mark.parametrize(
    ("robots", "allowed"),
    [
        (httpx.Response(404), True),
        (httpx.Response(410), True),
        (httpx.Response(403), False),
        (httpx.Response(401), False),
        (httpx.Response(503), False),
        (httpx.ConnectError("down"), False),
        (httpx.Response(200, text="User-agent: clapp-discovery\nDisallow: /\n"), False),
        (httpx.Response(200, text="User-agent: otherbot\nDisallow: /\n"), True),
    ],
)
async def test_robots_txt_answers(fetcher, robots, allowed):
    with respx.mock as router:
        route = router.get("https://fest.example/robots.txt")
        if isinstance(robots, Exception):
            route.mock(side_effect=robots)
        else:
            route.mock(return_value=robots)
        page_route = router.get("https://fest.example/").respond(
            200, content=fixture_bytes("calendar.html"), headers=HTML
        )

        if allowed:
            page = await fetcher.fetch("https://fest.example/")
            assert page.status == 200
        else:
            with pytest.raises(FetchError) as exc:
                await fetcher.fetch("https://fest.example/")
            assert exc.value.reason == "robots"
            assert not page_route.called


async def test_http_errors_raise_and_are_not_cached(web, fetcher):
    missing = web.get(f"{SITE}/gone/").respond(404, text="not found", headers=HTML)

    for _ in range(2):
        with pytest.raises(FetchError) as exc:
            await fetcher.fetch(f"{SITE}/gone/")
        assert exc.value.reason == "http_status"
    assert missing.call_count == 2


async def test_network_errors_raise(web, fetcher):
    web.get(f"{SITE}/slow/").mock(side_effect=httpx.ReadTimeout("timeout"))
    with pytest.raises(FetchError) as exc:
        await fetcher.fetch(f"{SITE}/slow/")
    assert exc.value.reason == "network"


async def test_non_html_is_refused(web, fetcher):
    web.get(f"{SITE}/flyer").respond(
        200, content=b"%PDF-1.4", headers={"content-type": "application/pdf"}
    )
    with pytest.raises(FetchError) as exc:
        await fetcher.fetch(f"{SITE}/flyer")
    assert exc.value.reason == "not_html"


async def test_redirects_are_followed(web, fetcher):
    web.get(f"{SITE}/dates").respond(301, headers={"location": f"{SITE}/agenda/"})
    page = await fetcher.fetch(f"{SITE}/dates")
    assert page.url == f"{SITE}/dates"
    assert page.final_url == f"{SITE}/agenda/"
    assert "Chalon dans la Rue" in page.text


async def test_large_pages_are_truncated(web, tmp_path):
    settings = Settings(
        _env_file=None, cache_dir=str(tmp_path), per_domain_interval_seconds=0, max_page_bytes=500
    )
    web.get(f"{SITE}/big/").respond(
        200, content=b"<html><body>" + b"<p>festival</p>" * 1000 + b"</body></html>", headers=HTML
    )
    fetcher = Fetcher(settings)
    page = await fetcher.fetch(f"{SITE}/big/")
    await fetcher.aclose()
    assert page.truncated
    assert len(page.html) <= 500


async def test_javascript_only_pages_are_empty(web, fetcher):
    web.get(f"{SITE}/app/").respond(200, content=fixture_bytes("js_only.html"), headers=HTML)
    page = await fetcher.fetch(f"{SITE}/app/")
    assert page.is_empty
    assert page.title == "Loading…"


async def test_charset_from_meta_tag(fetcher):
    with respx.mock as router:
        router.get("https://festival-des-rues.be/robots.txt").respond(404)
        router.get("https://festival-des-rues.be/contact/").respond(
            200,
            content=fixture_bytes("festival_contact.html"),
            headers={"content-type": "text/html"},
        )
        page = await fetcher.fetch("https://festival-des-rues.be/contact/")
    assert "Appel à candidatures 2027" in page.text


async def test_short_listing_pages_keep_their_text(web, fetcher):
    """trafilatura can drop short pages; the visible text is used instead."""
    page = await fetcher.fetch(f"{SITE}/")
    assert "Compagnie Les Jongleurs" in page.text


async def test_pages_count_against_the_budget_including_cache_hits(web, fetcher, settings):
    budget = RunBudget(Settings(_env_file=None, max_pages=2))
    await fetcher.fetch(f"{SITE}/agenda/", budget)
    await fetcher.fetch(f"{SITE}/agenda/", budget)
    with pytest.raises(BudgetExceeded):
        await fetcher.fetch(f"{SITE}/", budget)
    assert budget.counters["pages"] == 2


async def test_requests_to_one_domain_are_spaced_out(web, tmp_path):
    settings = Settings(
        _env_file=None, cache_dir=str(tmp_path), cache_ttl_days=0, per_domain_interval_seconds=0.2
    )
    fetcher = Fetcher(settings)
    start = time.monotonic()
    await fetcher.fetch(f"{SITE}/")  # robots.txt + page
    await fetcher.fetch(f"{SITE}/agenda/")
    elapsed = time.monotonic() - start
    await fetcher.aclose()
    assert elapsed >= 0.38  # three requests, two waits of 0.2s


@pytest.mark.parametrize(
    "url", ["", "mailto:a@b.c", "javascript:void(0)", "ftp://x.org/", "/agenda/"]
)
def test_invalid_urls(url):
    with pytest.raises(FetchError) as exc:
        clean_url(url)
    assert exc.value.reason == "invalid_url"

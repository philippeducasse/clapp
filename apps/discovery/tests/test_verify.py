import pytest

from discovery.tools.fetch import Page
from discovery.tools.verify import (
    SeenContent,
    extract_emails,
    is_blocklisted,
    url_key,
    verified_emails,
    verified_url,
    verified_website,
)
from tests.conftest import fixture_bytes, fixture_text

CONTACT_HTML = fixture_bytes("festival_contact.html").decode("iso-8859-1")


@pytest.mark.parametrize(
    "url",
    [
        "https://www.facebook.com/strassenfest",
        "https://m.facebook.com/x",
        "instagram.com/fest",
        "https://fr.wikipedia.org/wiki/Chalon_dans_la_rue",
        "https://www.eventbrite.fr/e/123",
        "https://www.billetweb.fr/fest",
        "https://www.lemonde.fr/culture/article.html",
        "https://linktr.ee/fest",
    ],
)
def test_blocklisted_hosts(url):
    assert is_blocklisted(url)


@pytest.mark.parametrize(
    "url",
    ["https://chalondanslarue.com/", "https://www.festival-des-rues.be/", "notfacebook.com", ""],
)
def test_organisation_sites_are_not_blocklisted(url):
    assert not is_blocklisted(url)


def test_extract_emails_handles_mailto_and_obfuscation():
    assert extract_emails(CONTACT_HTML) == {
        "programmation@festival-des-rues.be",
        "presse@festival-des-rues.be",
    }


@pytest.mark.parametrize(
    ("content", "expected"),
    [
        ("Write to Info@Fest.ORG.", {"info@fest.org"}),
        ("info(at)fest(dot)org", {"info@fest.org"}),
        ("info [at] fest.co.uk", {"info@fest.co.uk"}),
        ("info{arobase}fest{point}fr", {"info@fest.fr"}),
        ('<a href="mailto:info%40fest.org">mail</a>', {"info@fest.org"}),
        ("info&#64;fest.org", {"info@fest.org"}),
        ('<img src="logo@2x.png">', set()),
        ("you@example.com", set()),
        ("0123456789abcdef0123456789abcdef@o1.ingest.sentry.io", set()),
        ("no email here", set()),
    ],
)
def test_extract_emails_cases(content, expected):
    assert extract_emails(content) == expected


def test_url_key_ignores_scheme_www_fragment_and_trailing_slash():
    assert url_key("https://www.Fest.be/Contact/#form") == url_key("http://fest.be/Contact")
    assert url_key("https://fest.be/?id=2") != url_key("https://fest.be/?id=3")


@pytest.fixture
def seen() -> SeenContent:
    seen = SeenContent()
    seen.add_page(
        "https://festival-des-rues.be/contact/",
        html=CONTACT_HTML,
        text="Programmation : programmation [at] festival-des-rues [dot] be",
    )
    seen.add_page(
        "https://lesjongleurs.fr/agenda/",
        html=fixture_text("calendar.html"),
        final_url="https://www.lesjongleurs.fr/agenda/",
    )
    seen.add_urls(["https://from-search.org/page"])
    return seen


def test_only_emails_seen_in_fetched_content_are_kept(seen):
    assert verified_emails(
        [
            "PROGRAMMATION@festival-des-rues.be",
            "mailto:presse@festival-des-rues.be",
            "programmation@festival-des-rues.be",  # duplicate
            "contact@festival-des-rues.be",  # invented
            "",
        ],
        seen,
    ) == ["programmation@festival-des-rues.be", "presse@festival-des-rues.be"]


def test_only_urls_seen_are_kept(seen):
    assert verified_url("https://festival-des-rues.be/contact", seen)
    assert verified_url("https://www.lesjongleurs.fr/agenda/", seen)  # final url
    assert verified_url("https://chalondanslarue.com/", seen)  # linked from a fetched page
    assert verified_url("https://from-search.org/page", seen)  # search citation
    assert verified_url("https://chalondanslarue.com/candidatures/", seen) == ""  # invented
    assert verified_url("", seen) == ""


def test_verified_website_accepts_any_page_of_a_seen_site_but_no_blocklisted_host(seen):
    assert (
        verified_website("https://festival-des-rues.be/", seen) == "https://festival-des-rues.be/"
    )
    assert verified_website("https://www.festival-des-rues.be", seen)
    assert (
        verified_website("https://www.facebook.com/strassenfest", seen) == ""
    )  # linked, but blocklisted
    assert verified_website("https://never-seen.org/", seen) == ""


def test_seen_content_from_a_fetched_page():
    page = Page(
        url="https://fest.be/c",
        final_url="https://fest.be/contact",
        status=200,
        html='<a href="mailto:hello@fest.be">Hello</a>',
        text="Hello",
    )
    seen = SeenContent()
    seen.add_page(page.url, page.html, page.text, page.final_url)
    assert seen.has_email("hello@fest.be")
    assert seen.has_url("https://fest.be/c")
    assert seen.has_url("https://fest.be/contact")

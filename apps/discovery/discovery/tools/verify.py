"""Blocklisted hosts and verification of facts against pages the workflow fetched itself.

Nothing the LLM writes is trusted on its own: an email or URL is kept only if it appears in
content the workflow fetched (pages, search citations). Emails are never invented.

Blocklisted hosts (social networks, ticketing, encyclopedias, news, listings) are never used as an
organisation's `website_url`; they can still be visited as sources.
"""

import re
from collections.abc import Iterable
from urllib.parse import unquote, urldefrag, urlsplit

from discovery.tools.domains import domain_of, host_matches

# A host matches when it is one of these or a subdomain of one.
# fmt: off
BLOCKLISTED_HOSTS: frozenset[str] = frozenset({
    # social networks, video, link-in-bio
    "facebook.com", "fb.com", "fb.me", "instagram.com", "twitter.com", "x.com", "tiktok.com",
    "youtube.com", "youtu.be", "vimeo.com", "linkedin.com", "pinterest.com", "threads.net",
    "bsky.app", "mastodon.social", "soundcloud.com", "bandcamp.com", "spotify.com",
    "linktr.ee", "flickr.com", "tumblr.com", "medium.com", "t.me", "whatsapp.com",
    # ticketing and event listings
    "eventbrite.com", "eventbrite.fr", "eventbrite.de", "eventbrite.co.uk", "eventbrite.be",
    "eventbrite.es", "eventbrite.it", "eventbrite.nl", "ticketmaster.com", "ticketmaster.fr",
    "ticketmaster.de", "fnacspectacles.com", "billetreduc.com", "billetweb.fr",
    "weezevent.com", "helloasso.com", "yurplan.com", "seetickets.com", "eventim.de",
    "eventim.com", "dice.fm", "songkick.com", "bandsintown.com", "allevents.in",
    "infoconcert.com", "shotgun.live", "festicket.com", "tickettailor.com", "ticketswap.com",
    "openagenda.com", "meetup.com",
    # encyclopedias, search, maps
    "wikipedia.org", "wikimedia.org", "wikidata.org", "google.com", "goo.gl", "bing.com",
    "duckduckgo.com", "openstreetmap.org", "tripadvisor.com", "tripadvisor.fr", "yelp.com",
    # news
    "lemonde.fr", "liberation.fr", "lefigaro.fr", "francebleu.fr", "radiofrance.fr",
    "ouest-france.fr", "actu.fr", "ladepeche.fr", "leparisien.fr", "20minutes.fr",
    "telerama.fr", "lesoir.be", "rtbf.be", "lalibre.be", "vrt.be", "standaard.be",
    "spiegel.de", "zeit.de", "sueddeutsche.de", "faz.net", "bbc.co.uk", "bbc.com",
    "theguardian.com", "nytimes.com", "elpais.com", "repubblica.it", "corriere.it",
    # file and site hosting that isn't an organisation's own site
    "drive.google.com", "docs.google.com", "forms.gle", "dropbox.com", "wetransfer.com",
    "issuu.com", "calameo.com", "canva.com",
})
# fmt: on

# Placeholder and technical addresses that show up in page source but aren't contacts.
IGNORED_EMAIL_DOMAINS = frozenset(
    {"example.com", "example.org", "domain.com", "email.com", "sentry.io", "wixpress.com"}
)
IGNORED_EMAIL_SUFFIXES = (".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg")

_EMAIL = re.compile(r"[a-z0-9][a-z0-9._%+-]*@[a-z0-9-]+(?:\.[a-z0-9-]+)*\.[a-z]{2,}", re.IGNORECASE)
# "name [at] domain [dot] org", "name(at)domain.org", "name at domain dot org" (with brackets).
_OBFUSCATED = re.compile(
    r"([a-z0-9][a-z0-9._%+-]*)\s*[\[\(\{]\s*(?:at|arobase|ät)\s*[\]\)\}]\s*"
    r"([a-z0-9-]+(?:\s*(?:[\[\(\{]\s*(?:dot|point|punkt)\s*[\]\)\}]|\.)\s*[a-z0-9-]+)+)",
    re.IGNORECASE,
)
_OBFUSCATED_DOT = re.compile(
    r"\s*(?:[\[\(\{]\s*(?:dot|point|punkt)\s*[\]\)\}]|\.)\s*", re.IGNORECASE
)
_URL = re.compile(r"https?://[^\s<>\"'()\[\]]+", re.IGNORECASE)
_HREF = re.compile(r"""href\s*=\s*["']([^"']+)["']""", re.IGNORECASE)


def is_blocklisted(url_or_host: str) -> bool:
    return host_matches(domain_of(url_or_host), BLOCKLISTED_HOSTS)


def extract_emails(content: str) -> set[str]:
    """Email addresses in text or HTML, lowercased. Handles mailto: links, %40 and simple
    "[at]" / "(dot)" obfuscation. Image file names and placeholder domains are dropped."""
    content = unquote(content.replace("&#64;", "@").replace("&#x40;", "@"))
    found = {m.group(0) for m in _EMAIL.finditer(content)}
    for match in _OBFUSCATED.finditer(content):
        found.add(f"{match.group(1)}@{_OBFUSCATED_DOT.sub('.', match.group(2))}")
    return {email for e in found if _usable_email(email := e.lower().strip(".-"))}


def normalize_email(email: str) -> str:
    return (email or "").strip().lower().removeprefix("mailto:").split("?", 1)[0]


def url_key(url: str) -> str:
    """Comparison key for URLs: no scheme, no www., no fragment, no trailing slash."""
    url = urldefrag((url or "").strip())[0]
    if "://" not in url:
        url = f"https://{url}"
    parts = urlsplit(url)
    host = (parts.hostname or "").lower().removeprefix("www.")
    path = unquote(parts.path).rstrip("/")
    return f"{host}{path}{'?' + parts.query if parts.query else ''}"


class SeenContent:
    """Everything the workflow fetched itself during a run: pages and search citations.

    `has_email` / `has_url` answer "did we see this?", so extracted facts can be checked.
    """

    def __init__(self) -> None:
        self.emails: set[str] = set()
        self.urls: set[str] = set()  # url_key()s
        self.hosts: set[str] = set()

    def add_page(self, url: str, html: str = "", text: str = "", final_url: str = "") -> None:
        for page_url in (url, final_url):
            if page_url:
                self._add_url(page_url)
        for content in (html, text):
            if not content:
                continue
            self.emails |= extract_emails(content)
            for found in _URL.findall(content):
                self._add_url(found.rstrip(".,;:"))
        # Relative links are resolved by the caller (links.extract_links) if needed; absolute
        # hrefs are picked up here.
        for href in _HREF.findall(html or ""):
            if href.lower().startswith(("http://", "https://")):
                self._add_url(href)

    def add_urls(self, urls: Iterable[str]) -> None:
        for url in urls:
            self._add_url(url)

    def has_email(self, email: str) -> bool:
        return normalize_email(email) in self.emails

    def has_url(self, url: str) -> bool:
        return bool(url) and url_key(url) in self.urls

    def has_host(self, url: str) -> bool:
        return bool(url) and domain_of(url) in self.hosts

    def _add_url(self, url: str) -> None:
        key = url_key(url)
        if key:
            self.urls.add(key)
            self.hosts.add(domain_of(url))


def verified_emails(emails: Iterable[str], seen: SeenContent) -> list[str]:
    """The emails that appear in fetched content, normalized, in order, without duplicates."""
    kept: list[str] = []
    for email in emails:
        email = normalize_email(email)
        if email and seen.has_email(email) and email not in kept:
            kept.append(email)
    return kept


def verified_url(url: str, seen: SeenContent) -> str:
    """`url` if it appears in fetched content (or one of its pages was fetched), else ""."""
    if not url:
        return ""
    if seen.has_url(url):
        return url
    return ""


def verified_website(url: str, seen: SeenContent) -> str:
    """Like `verified_url`, for an organisation's own site: blocklisted hosts are refused, and
    a site counts as seen when any of its pages was fetched or linked."""
    if not url or is_blocklisted(url):
        return ""
    if seen.has_url(url) or seen.has_host(url):
        return url
    return ""


def _usable_email(email: str) -> bool:
    if "@" not in email or email.endswith(IGNORED_EMAIL_SUFFIXES):
        return False
    local, _, domain = email.rpartition("@")
    if not local or domain in IGNORED_EMAIL_DOMAINS:
        return False
    # Hashed tracking addresses (e.g. 32 hex chars @ sentry) aren't contacts.
    return not re.fullmatch(r"[0-9a-f]{24,}", local)

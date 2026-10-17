"""Links on a page: extract the same-site ones and rank them for a goal.

`navigate` (step 5) ranks with keywords first and only asks the LLM to pick a link (by number)
when no link clearly matches.
"""

import re
import unicodedata
from collections.abc import Iterable, Sequence
from typing import Literal
from urllib.parse import unquote, urldefrag, urlsplit

import lxml.html
from lxml import etree
from pydantic import BaseModel

from discovery.tools.domains import same_site

Goal = Literal["calendar", "contact", "application"]

# Keywords in several languages (en, fr, de, nl, es, it, pt). Matched against the words of the
# anchor text and of the URL path, after lowercasing and removing accents. Single words must
# match a whole word (so "date" doesn't match "datenschutz"); phrases match anywhere.
# fmt: off
KEYWORDS: dict[Goal, tuple[str, ...]] = {
    "calendar": (
        "agenda", "agendas", "dates", "date", "tour", "touring", "tournee", "tournees",
        "tour dates", "tourdates", "calendar", "calendrier", "calendario", "kalender",
        "termine", "tourtermine", "spielplan", "spieltermine", "upcoming", "shows", "gigs",
        "concerts", "events", "evenements", "programme", "program", "programma",
        "speellijst", "speeldata", "voorstellingen", "fechas", "gira", "giras", "bolos",
        "archive", "archives", "past shows", "past dates", "historique",
    ),
    "contact": (
        "contact", "contacts", "kontakt", "contacto", "contactos", "contatti", "contato",
        "impressum", "imprint", "mentions legales", "about", "about us", "a propos",
        "qui sommes nous", "equipe", "team", "ueber uns", "uber uns", "over ons",
        "quienes somos", "chi siamo", "organisation", "organization", "press", "presse",
        "pro", "pros", "professionnels", "professionals",
    ),
    "application": (
        "candidature", "candidatures", "candidater", "postuler", "appel", "appels",
        "appel a projets", "appel a candidatures", "open call", "open calls", "call for",
        "apply", "application", "applications", "bewerbung", "bewerbungen", "bewerben",
        "ausschreibung", "aanmelden", "aanmelding", "inschrijven", "convocatoria",
        "convocatorias", "bando", "inscription", "inscriptions", "participate", "participer",
        "submit", "submission", "submissions", "artists", "artistes", "kunstler", "residency",
        "residence", "residences", "residencies",
    ),
}

TEXT_WEIGHT = 3.0
URL_WEIGHT = 2.0
DEPTH_PENALTY = 0.25  # per path segment beyond the first: prefer /agenda over /agenda/2019/x

SKIPPED_SCHEMES = ("mailto:", "tel:", "javascript:", "data:", "sms:", "whatsapp:")
SKIPPED_EXTENSIONS = (
    ".jpg", ".jpeg", ".png", ".gif", ".svg", ".webp", ".ico", ".pdf", ".doc", ".docx",
    ".xls", ".xlsx", ".zip", ".rar", ".mp3", ".mp4", ".mov", ".avi", ".wav", ".ics",
    ".css", ".js", ".xml", ".rss",
)
# fmt: on

_WORDS = re.compile(r"[a-z0-9]+")


class Link(BaseModel):
    url: str
    text: str = ""
    score: float = 0.0


def extract_links(html: str, base_url: str, same_site_only: bool = True) -> list[Link]:
    """Links on the page, absolute, without #fragments or duplicates, in page order.

    Mail/phone/script links and files (images, PDFs, …) are dropped. With `same_site_only`,
    only links to the same registrable domain as `base_url` are kept (subdomains included).
    """
    if not html.strip():
        return []
    try:
        tree = lxml.html.fromstring(html)
        tree.make_links_absolute(base_url, resolve_base_href=True, handle_failures="discard")
    except (etree.ParserError, ValueError):
        return []

    base = _key(base_url)
    links: dict[str, Link] = {}
    for anchor in tree.iter("a"):
        href = (anchor.get("href") or "").strip()
        if not href or href.lower().startswith(SKIPPED_SCHEMES):
            continue
        url = urldefrag(href)[0]
        parts = urlsplit(url)
        if parts.scheme not in ("http", "https") or not parts.hostname:
            continue
        if parts.path.lower().endswith(SKIPPED_EXTENSIONS):
            continue
        if same_site_only and not same_site(url, base_url):
            continue
        key = _key(url)
        if key == base:
            continue
        text = _anchor_text(anchor)
        existing = links.get(key)
        if existing is None:
            links[key] = Link(url=url, text=text)
        elif len(text) > len(existing.text):
            existing.text = text
    return list(links.values())


def rank_links(
    links: Iterable[Link], goals: Sequence[Goal], extra_keywords: Sequence[str] = ()
) -> list[Link]:
    """Score every link for the goals and return them best first (ties keep page order).

    Links that match no keyword get a score of 0 and come last.
    """
    keywords = [k for goal in goals for k in KEYWORDS[goal]] + [
        " ".join(_WORDS.findall(_normalize(k))) for k in extra_keywords
    ]
    words = {k for k in keywords if " " not in k}
    phrases = [k for k in keywords if " " in k]

    scored: list[Link] = []
    for link in links:
        text = _normalize(link.text)
        path = _normalize(unquote(urlsplit(link.url).path).replace("-", " ").replace("_", " "))
        score = TEXT_WEIGHT * _matches(text, words, phrases) + URL_WEIGHT * _matches(
            path, words, phrases
        )
        if score > 0:
            depth = len([segment for segment in urlsplit(link.url).path.split("/") if segment])
            score = max(0.1, score - DEPTH_PENALTY * max(0, depth - 1))
        scored.append(link.model_copy(update={"score": score}))
    return sorted(scored, key=lambda link: -link.score)


def _matches(value: str, words: set[str], phrases: list[str]) -> int:
    """Number of distinct keywords found in `value` (an already normalized string)."""
    tokens = set(_WORDS.findall(value))
    spaced = " ".join(_WORDS.findall(value))
    return len(tokens & words) + sum(1 for phrase in phrases if phrase in spaced)


def _normalize(value: str) -> str:
    """Lowercase, accents removed: "Calendrier — Tournée" -> "calendrier — tournee"."""
    decomposed = unicodedata.normalize("NFKD", value.casefold())
    return "".join(c for c in decomposed if not unicodedata.combining(c))


def _anchor_text(anchor: lxml.html.HtmlElement) -> str:
    text = " ".join(anchor.text_content().split())
    if not text:
        text = anchor.get("title") or anchor.get("aria-label") or ""
    if not text:
        alts = [img.get("alt", "") for img in anchor.iter("img")]
        text = " ".join(a for a in alts if a)
    return " ".join(text.split())[:200]


def _key(url: str) -> str:
    """Comparison key: no scheme, no www., no trailing slash, lowercase host."""
    parts = urlsplit(urldefrag(url)[0])
    host = (parts.hostname or "").removeprefix("www.")
    path = parts.path.rstrip("/")
    return f"{host}{path}{'?' + parts.query if parts.query else ''}"

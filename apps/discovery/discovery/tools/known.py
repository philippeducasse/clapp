"""What clapp already has, so leads it knows aren't researched or proposed again.

The backend's `GET /internal/discovery/known-index/` returns ~600 short rows (seeds, superusers'
organisations, every candidate). `KnownIndex` loads them once per run and matches a lead by:

1. domain (host without "www.")
2. registrable domain (`en.festival.org` matches `festival.org`)
3. a fuzzy name match (rapidfuzz, ≥ 90) within the same country. When the lead or the entry has
   no country, only an exact (normalized) name match counts.

Blocklisted hosts (Facebook pages, ticketing sites, …) are shared by unrelated organisations, so
they're never used for domain matching.
"""

import re
import unicodedata
from collections import defaultdict
from typing import Literal

from pydantic import BaseModel
from rapidfuzz import fuzz, process

from discovery.backend_client import BackendClient, KnownEntry
from discovery.tools.domains import domain_of, registrable_domain
from discovery.tools.verify import is_blocklisted

NAME_THRESHOLD = 90

MatchReason = Literal["domain", "registrable_domain", "name"]

_YEAR = re.compile(r"\b(19|20)\d{2}\b")
_NON_WORD = re.compile(r"[\W_]+")


class KnownMatch(BaseModel):
    entry: KnownEntry
    reason: MatchReason
    score: float = 100.0


def normalize_name(name: str) -> str:
    """Casefolded, no accents, no punctuation, no years: "Chalon dans la Rue 2026!" ->
    "chalon dans la rue", "Straßenfest" -> "strassenfest"."""
    decomposed = unicodedata.normalize("NFKD", (name or "").casefold())
    ascii_name = "".join(c for c in decomposed if not unicodedata.combining(c))
    return " ".join(_NON_WORD.sub(" ", _YEAR.sub(" ", ascii_name)).split())


def normalize_country(country: str) -> str:
    return normalize_name(country)


class KnownIndex:
    def __init__(self, entries: list[KnownEntry] | None = None):
        self.entries: list[KnownEntry] = []
        self._by_domain: dict[str, KnownEntry] = {}
        self._by_registrable: dict[str, KnownEntry] = {}
        self._names_by_country: dict[str, list[tuple[str, KnownEntry]]] = defaultdict(list)
        self._by_exact_name: dict[str, KnownEntry] = {}
        for entry in entries or []:
            self.add(entry)

    @classmethod
    async def load(cls, backend: BackendClient) -> "KnownIndex":
        return cls(await backend.known_index())

    def __len__(self) -> int:
        return len(self.entries)

    def add(self, entry: KnownEntry) -> None:
        """Add an entry, e.g. a lead found earlier in the same run."""
        self.entries.append(entry)
        domain = domain_of(entry.domain)
        if domain and not is_blocklisted(domain):
            self._by_domain.setdefault(domain, entry)
            self._by_registrable.setdefault(registrable_domain(domain), entry)
        name = normalize_name(entry.name)
        if name:
            self._by_exact_name.setdefault(name, entry)
            country = normalize_country(entry.country)
            if country:
                self._names_by_country[country].append((name, entry))

    def match(self, name: str, country: str = "", website_url: str = "") -> KnownMatch | None:
        """The known entry this lead is, or None if clapp doesn't have it."""
        domain = domain_of(website_url)
        if domain and not is_blocklisted(domain):
            if entry := self._by_domain.get(domain):
                return KnownMatch(entry=entry, reason="domain")
            if entry := self._by_registrable.get(registrable_domain(domain)):
                return KnownMatch(entry=entry, reason="registrable_domain")

        normalized = normalize_name(name)
        if not normalized:
            return None
        country_key = normalize_country(country)
        candidates = self._names_by_country.get(country_key, []) if country_key else []
        if candidates:
            best = process.extractOne(
                normalized,
                [candidate_name for candidate_name, _ in candidates],
                scorer=fuzz.token_sort_ratio,
                score_cutoff=NAME_THRESHOLD,
            )
            if best is not None:
                _, score, index = best
                return KnownMatch(entry=candidates[index][1], reason="name", score=score)

        entry = self._by_exact_name.get(normalized)
        if entry is not None and (
            not country_key
            or not normalize_country(entry.country)
            or normalize_country(entry.country) == country_key
        ):
            return KnownMatch(entry=entry, reason="name")
        return None

    def is_known(self, name: str, country: str = "", website_url: str = "") -> bool:
        return self.match(name, country, website_url) is not None

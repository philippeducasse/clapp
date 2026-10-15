"""What clapp already knows, so discovery doesn't propose organisations twice."""

from typing import Iterable, Iterator, TypedDict

from django.db.models import Q

from discovery.models import DiscoveryCandidate
from organisations.festivals.models import Festival
from organisations.residencies.models import Residency
from organisations.utils import normalize_domain
from organisations.venues.models import Venue

ORG_MODELS = {
    DiscoveryCandidate.OrgType.FESTIVAL: Festival,
    DiscoveryCandidate.OrgType.RESIDENCY: Residency,
    DiscoveryCandidate.OrgType.VENUE: Venue,
}


class KnownEntry(TypedDict):
    name: str
    country: str
    town: str
    domain: str
    org_type: str
    source: str  # SEED | SUPERUSER | CANDIDATE


def _norm(value: str | None) -> str:
    return (value or "").strip().lower()


def known_index() -> list[KnownEntry]:
    """Seeds, organisations owned by superusers, and every existing candidate."""
    return list(_iter_known())


def _iter_known() -> Iterator[KnownEntry]:
    shared = Q(user__isnull=True) | Q(user__is_superuser=True)
    for org_type, model in ORG_MODELS.items():
        rows = model.objects.filter(shared).values_list(
            "name", "country", "town", "website_url", "user_id"
        )
        for name, country, town, website_url, user_id in rows:
            yield KnownEntry(
                name=name,
                country=country,
                town=town,
                domain=normalize_domain(website_url),
                org_type=org_type,
                source="SEED" if user_id is None else "SUPERUSER",
            )

    for name, country, town, domain, org_type in DiscoveryCandidate.objects.values_list(
        "name", "country", "town", "domain", "org_type"
    ):
        yield KnownEntry(
            name=name,
            country=country,
            town=town,
            domain=domain,
            org_type=org_type,
            source="CANDIDATE",
        )


class KnownMatcher:
    """Exact matching (domain, or name + country) against the known index.

    The service does the fuzzy matching; this is the backend's safety net.
    """

    def __init__(self, entries: Iterable[KnownEntry]):
        self.domains: set[str] = set()
        self.names: set[tuple[str, str]] = set()
        for entry in entries:
            self.add(entry["name"], entry["country"], entry["domain"])

    def add(self, name: str, country: str, domain: str) -> None:
        if domain:
            self.domains.add(domain)
        if name:
            self.names.add((_norm(name), _norm(country)))

    def matches(self, name: str, country: str, domain: str) -> bool:
        return (bool(domain) and domain in self.domains) or (
            (_norm(name), _norm(country)) in self.names
        )

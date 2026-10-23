"""Small helpers about leads and candidates: same organisation?, country filter, merging."""

import re

from rapidfuzz import fuzz

from discovery.backend_client import CandidateContact, CandidateIn, Evidence
from discovery.graph.state import Lead
from discovery.tools.domains import domain_of
from discovery.tools.known import NAME_THRESHOLD, normalize_country, normalize_name
from discovery.tools.verify import is_blocklisted, url_key

MAX_CONTACTS = 3

# Matched against the email's local part and the role, as word stems (any language we see often).
# Who decides on bookings / applications comes first; press, tickets, admin, etc. last.
PREFERRED_CONTACT = re.compile(
    r"prog|book|artis|direc|direz|curat|kurat|apply|applica|candidat|bewerb|residen|open.?call|"
    r"diffusion"
)
UNWANTED_CONTACT = re.compile(
    r"press|presse|prensa|stampa|media|comm|ticket|billet|biglietter|taquill|kasse|shop|boutique|"
    r"tienda|store|job|recruit|hr\b|rh\b|career|emploi|volunt|benevol|webmaster|web|newsletter|"
    r"privacy|gdpr|rgpd|dpo|compta|account|factur|invoice|billing|admin|partner|sponsor|mecen|"
    r"noreply|no-reply|technique|tech\b|regie|security|securite"
)


def contact_priority(contact: CandidateContact) -> int:
    """Lower is better: 0 programming/booking/applications, 1 general or unknown, 2 unwanted."""
    local = contact.email.partition("@")[0].lower()
    role = contact.role.lower()
    if PREFERRED_CONTACT.search(role) or PREFERRED_CONTACT.search(local):
        return 0
    if UNWANTED_CONTACT.search(role) or UNWANTED_CONTACT.search(local):
        return 2
    return 1


def best_contacts(contacts: list[CandidateContact]) -> list[CandidateContact]:
    """At most MAX_CONTACTS contacts, one per email, the most useful first. Within the same
    priority the given order is kept (the LLM's own ranking)."""
    unique: list[CandidateContact] = []
    seen: set[str] = set()
    for contact in contacts:
        if contact.email and contact.email not in seen:
            seen.add(contact.email)
            unique.append(contact)
    return sorted(unique, key=contact_priority)[:MAX_CONTACTS]


def site_key(url: str) -> str:
    """Domain used to recognise an organisation, or "" (no URL, or a shared host like Facebook)."""
    domain = domain_of(url)
    return "" if not domain or is_blocklisted(domain) else domain


def same_org(
    name_a: str, country_a: str, url_a: str, name_b: str, country_b: str, url_b: str
) -> bool:
    """Same website, or names matching (fuzzy ≥ 90) with no conflicting country."""
    site_a, site_b = site_key(url_a), site_key(url_b)
    if site_a and site_a == site_b:
        return True
    a, b = normalize_name(name_a), normalize_name(name_b)
    if not a or not b:
        return False
    ca, cb = normalize_country(country_a), normalize_country(country_b)
    if ca and cb and ca != cb:
        return False
    if a == b:
        return True
    return bool(ca and cb) and fuzz.token_sort_ratio(a, b) >= NAME_THRESHOLD


def country_ok(country: str, countries: list[str]) -> bool:
    """True when no countries were asked for, the lead's country is unknown, or it matches."""
    if not countries or not country:
        return True
    return normalize_country(country) in {normalize_country(c) for c in countries}


def merge_lead(leads: list[Lead], lead: Lead) -> bool:
    """Add `lead` to `leads` unless it's already there; then fill the existing one's blanks.
    Returns True when it was added."""
    for existing in leads:
        if same_org(
            existing.name, existing.country, existing.website_url,
            lead.name, lead.country, lead.website_url,
        ):  # fmt: skip
            for field in ("town", "country", "dates", "website_url"):
                if not getattr(existing, field) and getattr(lead, field):
                    setattr(existing, field, getattr(lead, field))
            return False
    leads.append(lead)
    return True


def merge_evidence(*lists: list[Evidence]) -> list[Evidence]:
    """Concatenate, dropping repeated pages (first one wins)."""
    seen: set[str] = set()
    merged: list[Evidence] = []
    for evidence in (e for items in lists for e in items):
        key = url_key(evidence.url)
        if key not in seen:
            seen.add(key)
            merged.append(evidence)
    return merged


def candidate_rank(candidate: CandidateIn) -> tuple[int, int, int]:
    """Higher is better: reviewable first, then more contacts, then more facts."""
    filled = sum(
        bool(getattr(candidate, field))
        for field in (
            "website_url", "description", "town", "country", "start_date", "approximate_date",
            "application_type", "application_url",
        )
    )  # fmt: skip
    return (candidate.state == "PENDING", len(candidate.contacts), filled)


def dedupe_candidates(candidates: list[CandidateIn]) -> list[CandidateIn]:
    """One candidate per organisation: the best one, with the others' sources and contacts."""
    kept: list[CandidateIn] = []
    for candidate in candidates:
        for index, other in enumerate(kept):
            if not same_org(
                other.name, other.country, other.website_url,
                candidate.name, candidate.country, candidate.website_url,
            ):  # fmt: skip
                continue
            best, rest = (
                (candidate, other)
                if candidate_rank(candidate) > candidate_rank(other)
                else (other, candidate)
            )
            kept[index] = best.model_copy(
                update={
                    "sources": merge_evidence(best.sources, rest.sources),
                    "contacts": best_contacts(best.contacts + rest.contacts),
                }
            )
            break
        else:
            kept.append(candidate)
    return kept

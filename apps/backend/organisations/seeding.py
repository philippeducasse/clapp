"""Copying seed organisations (user=NULL) and their contacts into per-user rows.

Seeds are shared templates. Every user works on their own copy (`is_seed_clone=True`),
created at signup for all seeds, or later via `propagate_seed` for a single new seed.
"""

import logging
from collections import defaultdict
from dataclasses import dataclass
from typing import Iterable, Sequence

from django.db import models, transaction
from django.db.models import Q

from organisations.festivals.models import Festival, FestivalContact
from organisations.models import Organisation
from organisations.residencies.models import Residency, ResidencyContact
from organisations.utils import normalize_domain
from organisations.venues.models import Venue, VenueContact

logger = logging.getLogger(__name__)

_COMMON_FIELDS = ("name", "description", "country", "town", "website_url", "comments")
_DATE_FIELDS = (
    "start_date",
    "end_date",
    "approximate_date",
    "application_date_start",
    "application_date_end",
    "application_type",
)
_CONTACT_FIELDS = ("name", "email", "role", "phone")


@dataclass(frozen=True)
class SeedSpec:
    contact_model: type[models.Model]
    contact_fk: str
    fields: tuple[str, ...]


SEED_SPECS: dict[type[Organisation], SeedSpec] = {
    Festival: SeedSpec(
        FestivalContact, "festival", _COMMON_FIELDS + ("festival_type",) + _DATE_FIELDS
    ),
    Venue: SeedSpec(VenueContact, "venue", _COMMON_FIELDS + ("venue_type", "contacted")),
    Residency: SeedSpec(ResidencyContact, "residency", _COMMON_FIELDS + _DATE_FIELDS),
}


@transaction.atomic
def clone_seeds_for_profiles(
    model: type[Organisation], seeds: Iterable[Organisation], profiles: Iterable
) -> int:
    """Copy each seed (and its live contacts) to each profile. Returns the number of orgs created."""
    spec = SEED_SPECS[model]
    seeds = list(seeds)
    profiles = list(profiles)
    if not seeds or not profiles:
        return 0

    pairs = [(seed, profile) for profile in profiles for seed in seeds]
    clones = model.objects.bulk_create(
        [
            model(
                user=profile,
                is_seed_clone=True,
                # spread all fields out to create each entity
                **{field: getattr(seed, field) for field in spec.fields},
            )
            for seed, profile in pairs
        ]
    )

    contacts_by_seed: dict[int, list] = defaultdict(list)
    for contact in spec.contact_model.objects.filter(**{f"{spec.contact_fk}__in": seeds}):
        contacts_by_seed[getattr(contact, f"{spec.contact_fk}_id")].append(contact)

    # `clones` is in the same order as `pairs`, so clones[i] is the copy of pairs[i]'s seed.
    new_contacts = [
        spec.contact_model(
            user=profile,
            **{spec.contact_fk: clone},
            **{field: getattr(contact, field) for field in _CONTACT_FIELDS},
        )
        for (seed, profile), clone in zip(pairs, clones)
        for contact in contacts_by_seed[seed.id]
    ]

    if new_contacts:
        spec.contact_model.objects.bulk_create(new_contacts)

    logger.info(
        "Cloned %d %s seed(s) and %d contact(s) for %d profile(s)",
        len(seeds),
        model.__name__,
        len(new_contacts),
        len(profiles),
    )
    return len(clones)


def clone_all_seeds_for_profile(profile) -> None:
    """Give a (new) profile its own copy of every seed organisation."""
    for model in SEED_SPECS:
        clone_seeds_for_profiles(model, model.objects.filter(user__isnull=True), [profile])


def has_matching_organisation(model: type[Organisation], profile, seed: Organisation) -> bool:
    """True if `profile` already has an organisation matching `seed` (same domain, or name+country)."""
    owned = model.objects.filter(user=profile)
    name_match = Q(name__iexact=seed.name.strip()) & Q(country__iexact=(seed.country or "").strip())
    if owned.filter(name_match).exists():
        return True

    domain = normalize_domain(seed.website_url)
    if not domain:
        return False
    return any(
        normalize_domain(url) == domain
        for url in owned.filter(website_url__icontains=domain).values_list("website_url", flat=True)
    )


def propagate_seed_to_profiles(seed: Organisation, profiles: Sequence) -> int:
    """Copy one seed to every given profile that doesn't already have a matching organisation."""
    model = type(seed)
    if seed.user_id is not None:
        raise ValueError(f"{model.__name__} {seed.pk} is not a seed (user is set)")

    targets = [p for p in profiles if not has_matching_organisation(model, p, seed)]
    return clone_seeds_for_profiles(model, [seed], targets)

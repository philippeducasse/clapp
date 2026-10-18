"""Turning an accepted candidate into a shared seed organisation."""

from django.contrib.contenttypes.models import ContentType
from django.db import transaction
from django.db.models import F
from django.utils import timezone

from discovery.known import ORG_MODELS
from discovery.models import DiscoveryCandidate, DiscoverySource
from organisations.festivals.models import Festival
from organisations.models import Organisation
from organisations.seeding import SEED_SPECS
from organisations.tasks import propagate_seed
from organisations.utils import clean_organisation_data, normalize_domain
from organisations.venues.models import Venue

# Candidate fields the reviewer may change when accepting.
EDITABLE_FIELDS = (
    "org_type",
    "name",
    "description",
    "country",
    "town",
    "website_url",
    "subtype",
    "application_type",
)

ACCEPTABLE_STATES = (DiscoveryCandidate.State.PENDING, DiscoveryCandidate.State.UNRESOLVED)


class CannotAccept(Exception):
    pass


def _choice_or_default(model: type[Organisation], field_name: str, value: str) -> str:
    field = model._meta.get_field(field_name)
    valid = {key for key, _ in field.choices}
    return value if value in valid else field.default


def build_seed(candidate: DiscoveryCandidate) -> Organisation:
    """An unsaved seed (user=NULL) of the right type, filled from the candidate."""
    model = ORG_MODELS[candidate.org_type]
    seed = model(
        user=None,
        is_seed_clone=False,
        name=candidate.name,
        description=candidate.description,
        country=candidate.country,
        town=candidate.town,
        website_url=candidate.website_url,
    )
    if candidate.application_url:
        # Public information, so it's fine that comments are copied to every user.
        seed.comments = f"Application: {candidate.application_url}"

    if model is Venue:
        seed.venue_type = _choice_or_default(model, "venue_type", candidate.subtype)
        return seed

    seed.application_type = _choice_or_default(
        model, "application_type", candidate.application_type
    )
    for field in (
        "start_date",
        "end_date",
        "approximate_date",
        "application_date_start",
        "application_date_end",
    ):
        setattr(seed, field, getattr(candidate, field))
    if model is Festival:
        seed.festival_type = _choice_or_default(model, "festival_type", candidate.subtype)
        seed.estimated_start_date = candidate.estimated_start_date or candidate.start_date
    return seed


@transaction.atomic
def accept_candidate(candidate_id: int, overrides: dict | None = None) -> DiscoveryCandidate:
    """Create the seed and its contacts, then copy it to every user once the transaction commits.

    Accepting an already accepted candidate returns it unchanged.
    """
    candidate = DiscoveryCandidate.objects.select_for_update().get(pk=candidate_id)
    if candidate.state == DiscoveryCandidate.State.ACCEPTED and candidate.seed_object_id:
        return candidate
    if candidate.state not in ACCEPTABLE_STATES:
        raise CannotAccept(f"A {candidate.state.lower()} candidate can't be accepted.")

    for field, value in (overrides or {}).items():
        if field in EDITABLE_FIELDS:
            setattr(candidate, field, value)
    candidate.domain = normalize_domain(candidate.website_url)

    seed = build_seed(candidate)
    clean_organisation_data(seed)
    seed.save()

    contact_model = SEED_SPECS[type(seed)].contact_model
    contact_fk = SEED_SPECS[type(seed)].contact_fk
    contact_model.objects.bulk_create(
        [
            contact_model(
                user=None,
                name=(contact.get("name") or "")[:200],
                email=contact.get("email") or "",
                role=(contact.get("role") or "")[:100],
                **{contact_fk: seed},
            )
            for contact in candidate.contacts
            if contact.get("email") or contact.get("name")
        ]
    )

    candidate.state = DiscoveryCandidate.State.ACCEPTED
    candidate.dismiss_reason = ""
    candidate.reviewed_at = timezone.now()
    candidate.seed_content_type = ContentType.objects.get_for_model(seed)
    candidate.seed_object_id = seed.pk
    candidate.save()

    _credit_sources(candidate)
    label, seed_id = type(seed)._meta.label, seed.pk
    transaction.on_commit(lambda: propagate_seed.delay(label, seed_id))
    return candidate


def _credit_sources(candidate: DiscoveryCandidate) -> None:
    """Count the acceptance for the artist/aggregator sites that led to this candidate."""
    domains = {
        normalize_domain(step.get("url", ""))
        for step in candidate.found_via
        # The service writes kinds in lowercase ("artist_site"); older rows use uppercase.
        if (step.get("kind") or "").upper() in DiscoverySource.Kind.values
    } - {""}
    if domains:
        DiscoverySource.objects.filter(domain__in=domains).update(
            candidates_accepted=F("candidates_accepted") + 1
        )

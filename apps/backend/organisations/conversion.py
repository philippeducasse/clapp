"""Changing an organisation's type (e.g. a Festival that is really a Venue).

Types are separate tables, so conversion creates a new row of the target type and
deletes the old one. Everything pointing at the old organisation is moved over.
"""

from django.contrib.contenttypes.models import ContentType
from django.db import models, transaction

from applications.models import Application, InboundEmail
from discovery.models import DiscoveryCandidate
from organisations.festivals.models import Festival
from organisations.models import Organisation
from organisations.residencies.models import Residency
from organisations.venues.models import Venue
from profiles.models import Reminder

ORGANISATION_TYPES: dict[str, type[Organisation]] = {
    "FESTIVAL": Festival,
    "VENUE": Venue,
    "RESIDENCY": Residency,
}

# Never copied: the new row gets its own id, and only live organisations are converted.
_SKIPPED_FIELDS = {"id", "deleted_at"}

# Contact fields copied to the new organisation's contacts (the FK is set separately).
_CONTACT_FIELDS = ("name", "email", "role", "phone", "user", "is_seed_clone")


class ConversionError(Exception):
    pass


def _copyable_value(target_field: models.Field, value):
    """`value` if the target field accepts it, else the target's default (e.g. an invalid choice)."""
    if target_field.choices and value not in {key for key, _ in target_field.flatchoices}:
        return target_field.get_default()
    return value


def _build_target(source: Organisation, target_model: type[Organisation]) -> Organisation:
    """Unsaved organisation of `target_model` with every field both types share.

    Type-specific fields (festival_type, venue_type, dates on venues, ...) are dropped;
    choices the target doesn't support (e.g. a residency's OPEN_CALL on a festival) reset
    to the target's default.
    """
    target_fields = {f.name: f for f in target_model._meta.concrete_fields}
    values = {}
    for field in source._meta.concrete_fields:
        target_field = target_fields.get(field.name)
        if field.name in _SKIPPED_FIELDS or target_field is None:
            continue
        if field.get_internal_type() != target_field.get_internal_type():
            continue
        values[field.attname] = _copyable_value(target_field, getattr(source, field.attname))
    return target_model(**values)


def _repoint(model, ct_field: str, id_field: str, source_ct, source_id, target_ct, target_id):
    # _base_manager includes soft-deleted rows, which must move too.
    model._base_manager.filter(**{ct_field: source_ct, id_field: source_id}).update(
        **{ct_field: target_ct, id_field: target_id}
    )


@transaction.atomic
def convert_organisation(source: Organisation, target_type: str) -> Organisation:
    """Turn `source` into an organisation of `target_type` ("FESTIVAL", "VENUE" or "RESIDENCY").

    Copies shared fields and live contacts, moves applications, inbound emails, reminders
    and discovery links to the new organisation, then hard-deletes `source`.
    Returns the new organisation.
    """
    target_model = ORGANISATION_TYPES.get(target_type.upper())
    if target_model is None:
        raise ConversionError(
            f"Invalid organisation type. Must be one of: {', '.join(ORGANISATION_TYPES)}"
        )
    if isinstance(source, target_model):
        raise ConversionError(f"Organisation is already a {target_model.__name__.lower()}")
    if source.deleted_at is not None:
        raise ConversionError("Deleted organisations cannot be converted")

    target = _build_target(source, target_model)
    target.save()

    target_contact_model = target.contacts.model
    target_contact_fk = target.contacts.field.name
    target_contact_model.objects.bulk_create(
        [
            target_contact_model(
                **{target_contact_fk: target},
                **{field: getattr(contact, field) for field in _CONTACT_FIELDS},
            )
            for contact in source.contacts.all()  # live contacts only
        ]
    )

    source_ct = ContentType.objects.get_for_model(source.__class__)
    target_ct = ContentType.objects.get_for_model(target_model)
    ids = (source_ct, source.pk, target_ct, target.pk)
    _repoint(Application, "content_type", "object_id", *ids)
    _repoint(InboundEmail, "organisation_content_type", "organisation_id", *ids)
    _repoint(Reminder, "content_type", "object_id", *ids)
    _repoint(DiscoveryCandidate, "seed_content_type", "seed_object_id", *ids)

    # Hard delete: a soft-deleted original could be restored into a duplicate. Nothing
    # points at it any more, so this only removes the row and its old contacts.
    source.hard_delete()
    return target

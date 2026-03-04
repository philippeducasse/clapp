from typing import Any

from rest_framework import serializers


class OrganisationSerializerMixin(serializers.Serializer):
    """Mixin that adds user-created metadata fields to any organisation serializer.

    This inherits from serializers.Serializer (rather than being a plain Python
    class) because DRF uses a custom metaclass (SerializerMetaclass) that builds
    a _declared_fields dict at class-creation time. It does this by scanning the
    class body and then merging in _declared_fields from each base class. A plain
    Python class has no _declared_fields, so DRF silently skips it — the fields
    declared here would never make it into the serializer, causing
    ImproperlyConfigured at runtime.

    By inheriting from serializers.Serializer, DRF's metaclass processes this
    class and sets _declared_fields = {'is_user_created': ..., 'added_by': ...}.
    Subclasses then pick those up automatically during their own class creation.

    Both this mixin and WritableNestedModelSerializer ultimately inherit from
    Serializer (diamond inheritance), which Python's C3 MRO handles cleanly.

    Usage:
        class FestivalSerializer(OrganisationSerializerMixin, WritableNestedModelSerializer):
            class Meta:
                fields = [..., "is_user_created", "added_by"]

    The mixin is placed left of WritableNestedModelSerializer by convention:
    in Python's MRO (Method Resolution Order), leftmost wins when two bases define the same name.
    """

    # SerializerMethodField delegates serialization to get_<field_name>() below.
    # read_only is implied by SerializerMethodField — no write path needed.
    is_user_created = serializers.SerializerMethodField()
    added_by = serializers.SerializerMethodField()

    def get_is_user_created(self, obj: Any) -> bool:
        return obj.user_id is not None and not obj.is_seed_clone

    def get_added_by(self, obj: Any) -> str | None:
        if obj.user_id is not None and not obj.is_seed_clone:
            return obj.user.email
        return None


class BlankToNullDateField(serializers.DateField):
    """Convert blank strings to None for date fields."""

    def to_internal_value(self, data: Any) -> Any:
        if data in ("", None):
            return None
        return super().to_internal_value(data)


class BaseContactSerializer(serializers.ModelSerializer):
    """Generic contact serializer for any organisation contact type."""

    class Meta:
        fields = ["id", "name", "email"]


def handle_nested_contacts(
    instance: Any, contacts_data: Any, contact_model: type, user: Any = None
) -> None:
    """Handle creation, update, and deletion of nested contacts.

    Args:
        instance: The organisation instance (Festival, Residency, etc.)
        contacts_data: The contact data from validated_data
        contact_model: The contact model class (FestivalContact, ResidencyContact, etc.)
        user: The user who owns the organisation (used when creating new contacts)
    """
    existing_contacts = {c.id: c for c in instance.contacts.all()}
    incoming_ids = {c.get("id") for c in contacts_data if c.get("id")}

    # Delete contacts not in incoming data
    to_delete = set(existing_contacts.keys()) - incoming_ids
    contact_model.objects.filter(id__in=to_delete).delete()

    # Create or update contacts
    for contact_data in contacts_data:
        contact_id = contact_data.get("id")
        if contact_id and contact_id in existing_contacts:
            # Update existing
            for attr, value in contact_data.items():
                setattr(existing_contacts[contact_id], attr, value)
            existing_contacts[contact_id].save()
        else:
            # Create new - infer the foreign key field name
            fk_field = next(
                f
                for f in contact_model._meta.get_fields()
                if hasattr(f, "related_model") and f.related_model == instance.__class__
            )
            create_kwargs = {fk_field.name: instance, **contact_data}
            if user:
                create_kwargs["user"] = user
            contact_model.objects.create(**create_kwargs)

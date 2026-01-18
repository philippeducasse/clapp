from typing import Any

from rest_framework import serializers


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


def handle_nested_contacts(instance: Any, contacts_data: Any, contact_model: type) -> None:
    """Handle creation, update, and deletion of nested contacts.

    Args:
        instance: The organisation instance (Festival, Residency, etc.)
        contacts_data: The contact data from validated_data
        contact_model: The contact model class (FestivalContact, ResidencyContact, etc.)
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
            contact_model.objects.create(**{fk_field.name: instance, **contact_data})

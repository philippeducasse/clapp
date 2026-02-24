from typing import Any, Type

from drf_writable_nested.serializers import WritableNestedModelSerializer

from organisations.venues.models import Venue, VenueContact
from organisations.serializers import BaseContactSerializer, handle_nested_contacts
from clapp_backend.utils import NormalizedURLField


class VenueContactSerializer(BaseContactSerializer):
    class Meta(BaseContactSerializer.Meta):
        model = VenueContact


class VenueSerializer(WritableNestedModelSerializer):
    contacts = VenueContactSerializer(many=True, required=False)
    website_url = NormalizedURLField(required=False, allow_blank=True)

    class Meta:
        model: Type[Venue] = Venue
        fields = [
            "id",
            "name",
            "description",
            "country",
            "town",
            "website_url",
            "venue_type",
            "tag",
            "comments",
            "contacts",
            "deleted_at",
        ]
        read_only_fields = ("id", "deleted_at")

    def update(self, instance: Venue, validated_data: Venue) -> dict[str, Any]:
        contacts_data = validated_data.pop("contacts", None)

        # Update venue fields
        instance = super().update(instance, validated_data)

        if contacts_data is not None:
            handle_nested_contacts(instance, contacts_data, VenueContact, user=instance.user)

        return instance

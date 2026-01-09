from typing import Type

from rest_framework import serializers

from organisations.venues.models import Venue, VenueContact
from organisations.serializers import BaseContactSerializer
from circus_agent_backend.utils import NormalizedURLField


class VenueContactSerializer(BaseContactSerializer):
    class Meta(BaseContactSerializer.Meta):
        model = VenueContact


class VenueSerializer(serializers.ModelSerializer):
    website_url = NormalizedURLField(required=False, allow_blank=True)

    class Meta:
        model: Type[Venue] = Venue
        fields: str = "__all__"
        read_only_fields = ("id", "deleted_at")

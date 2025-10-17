from rest_framework import serializers
from organisations.venues.models import Venue
from typing import Type


class VenueSerializer(serializers.ModelSerializer):
    class Meta:
        model: Type[Venue] = Venue
        fields: str = "__all__"
        read_only_fields = ("id",)

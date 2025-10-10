from rest_framework import serializers
from venues.models import Venue


class VenueSerializer(serializers.ModelSerializer):
    class Meta:
        model: Type[Venue] = Venue
        fields: str = "__all__"
        read_only_fields = ("id",)

from rest_framework import serializers
from organisations.residencies.models import Residency
from typing import Type
from circus_agent_backend.utils import NormalizedURLField


class ResidencySerializer(serializers.ModelSerializer):
    website_url = NormalizedURLField(required=False, allow_blank=True)

    class Meta:
        model: Type[Residency] = Residency
        fields: str = "__all__"
        read_only_fields = ("id", "deleted_at")

from typing import Type

from rest_framework import serializers

from circus_agent_backend.utils import NormalizedURLField
from organisations.festivals.serializer import BlankToNullDateField
from organisations.residencies.models import Residency


class ResidencySerializer(serializers.ModelSerializer):
    website_url = NormalizedURLField(required=False, allow_blank=True)
    start_date = BlankToNullDateField(required=False, allow_null=True)
    end_date = BlankToNullDateField(required=False, allow_null=True)

    class Meta:
        model: Type[Residency] = Residency
        fields: str = "__all__"
        read_only_fields = ("id", "deleted_at")

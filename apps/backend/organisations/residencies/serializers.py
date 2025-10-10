from rest_framework import serializers
from organisations.residencies.models import Residency
from typing import Type


class ResidencySerializer(serializers.ModelSerializer):
    class Meta:
        model: Type[Residency] = Residency
        fields: str = "__all__"
        read_only_fields = ("id",)

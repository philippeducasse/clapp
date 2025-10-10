from rest_framework import serializers
from residencies.models import Residency


class ResidencySerializer(serializers.ModelSerializer):
    class Meta:
        model: Type[Residency] = Residency
        fields: str = "__all__"
        read_only_fields = ("id",)

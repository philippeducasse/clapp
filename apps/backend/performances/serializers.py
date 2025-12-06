from rest_framework import serializers
from performances.models import Performance
from typing import Type


class PerformanceSerializer(serializers.ModelSerializer):
    creation_date = serializers.DateField(allow_null=True, required=False)
    genres = serializers.ListField(
        child=serializers.CharField(),
        required=False,
        allow_empty=True
    )

    class Meta:
        model: Type[Performance] = Performance
        fields: str = "__all__"
        read_only_fields = ("id",)

from rest_framework import serializers
from profiles.models import Profile
from performances.serializers import PerformanceSerializer
from typing import Type


class ProfileSerializer(serializers.ModelSerializer):
    performances = PerformanceSerializer(many=True, read_only=True)

    class Meta:
        model: Type[Profile] = Profile
        exclude = ("password",)
        read_only_fields = ("id",)

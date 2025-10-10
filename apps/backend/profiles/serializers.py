from rest_framework import serializers
from profiles.models import Profile


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model: Type[Profile] = Profile
        fields: str = "__all__"
        read_only_fields = ("id",)

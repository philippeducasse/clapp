from rest_framework import serializers
from profiles.models import Profile
from performances.serializers import PerformanceSerializer
from typing import Type
import re


class ProfileSerializer(serializers.ModelSerializer):
    performances = PerformanceSerializer(many=True, read_only=True)
    spoken_languages = serializers.ListField(
        child=serializers.CharField(), required=False, allow_empty=True
    )

    class Meta:
        model: Type[Profile] = Profile
        exclude = ("password",)
        read_only_fields = ("id",)


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True)

    class Meta:
        model = Profile
        fields = [
            "email",
            "password",
            "password_confirm",
        ]

    def validate_password(self, value):
        """Validate password strength"""
        if not re.search(r"[A-Z]", value):
            raise serializers.ValidationError(
                "Password must contain at least one uppercase letter"
            )
        if not re.search(r"[a-z]", value):
            raise serializers.ValidationError(
                "Password must contain at least one lowercase letter"
            )
        if not re.search(r"\d", value):
            raise serializers.ValidationError(
                "Password must contain at least one digit"
            )
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', value):
            raise serializers.ValidationError(
                "Password must contain at least one special character"
            )
        return value

    def validate(self, data):
        if data["password"] != data["password_confirm"]:
            raise serializers.ValidationError("Passwords don't match!")
        return data

    def create(self, validated_data):
        validated_data.pop("password_confirm")
        return Profile.objects.create_user(**validated_data)

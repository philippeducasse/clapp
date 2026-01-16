from rest_framework import serializers
from profiles.models import EmailTemplate, Profile
from performances.serializers import PerformanceSerializer
from typing import Type
import re
from circus_agent_backend.utils import NormalizedURLField


class EmailTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmailTemplate
        fields = ["id", "name", "content"]
        read_only_fields = ["id"]


class ProfileSerializer(serializers.ModelSerializer):
    performances = PerformanceSerializer(many=True, read_only=True)
    spoken_languages = serializers.ListField(
        child=serializers.CharField(), required=False, allow_empty=True
    )
    email_templates = EmailTemplateSerializer(many=True)
    personal_website = NormalizedURLField(required=False, allow_blank=True)
    instagram_profile = NormalizedURLField(required=False, allow_blank=True)
    facebook_profile = NormalizedURLField(required=False, allow_blank=True)
    tiktok_profile = NormalizedURLField(required=False, allow_blank=True)
    youtube_profile = NormalizedURLField(required=False, allow_blank=True)

    class Meta:
        model: Type[Profile] = Profile
        exclude = ("password", "groups", "user_permissions")
        read_only_fields = ("id",)

    def update(self, instance, validated_data):
        email_templates = validated_data.pop("email_templates", [])
        email_templates_ids = validated_data.pop("email_templates_ids", [])

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if email_templates_ids is not None:
            instance.email_templates.exclude(id__in=email_templates_ids).delete()

        for email_template in email_templates:
            EmailTemplate.objects.create(profile=instance, **email_template)

        return instance


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
            raise serializers.ValidationError("Password must contain at least one uppercase letter")
        if not re.search(r"[a-z]", value):
            raise serializers.ValidationError("Password must contain at least one lowercase letter")
        if not re.search(r"\d", value):
            raise serializers.ValidationError("Password must contain at least one digit")
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

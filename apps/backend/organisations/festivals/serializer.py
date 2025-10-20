from rest_framework import serializers
from organisations.festivals.models import Festival, FestivalContact
from typing import List, Type, Any
from drf_writable_nested.serializers import WritableNestedModelSerializer


class BlankToNullDateField(serializers.DateField):
    def to_internal_value(self, data: Any) -> Any:
        if data in ("", None):
            return None
        return super().to_internal_value(data)


class FestivalContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = FestivalContact
        fields = ["id", "name", "email"]


class FestivalSerializer(WritableNestedModelSerializer):
    contacts = FestivalContactSerializer(many=True, required=False)

    start_date = BlankToNullDateField(required=False, allow_null=True)
    end_date = BlankToNullDateField(required=False, allow_null=True)

    has_application_this_year = serializers.BooleanField(read_only=True, required=False)
    latest_application_status = serializers.CharField(
        read_only=True, allow_null=True, required=False
    )
    latest_application_date = serializers.DateField(
        read_only=True, allow_null=True, required=False
    )

    # will look for this name + get
    current_year_application = serializers.SerializerMethodField()

    class Meta:
        model: Type[Festival] = Festival
        fields: List[str] = [
            "id",
            "name",
            "description",
            "country",
            "town",
            "festival_type",
            "website_url",
            # "contact_email",
            # "contact_person",
            "start_date",
            "end_date",
            "approximate_date",
            "application_date_start",
            "application_date_end",
            "application_type",
            "comments",
            "contacts",
            # Annotated fields
            "has_application_this_year",
            "latest_application_status",
            "latest_application_date",
            # Nested applications
            "current_year_application",
        ]

    def update(self, instance: Festival, validated_data: Festival) -> dict[str, Any]:
        contacts_data = validated_data.pop("contacts", None)

        # Update festival fields
        instance = super().update(instance, validated_data)

        # Handle contacts
        if contacts_data is not None:
            # Get existing contact IDs
            existing_contacts = {c.id: c for c in instance.contacts.all()}
            incoming_ids = {c.get("id") for c in contacts_data if c.get("id")}

            # Delete removed contacts
            to_delete = set(existing_contacts.keys()) - incoming_ids
            FestivalContact.objects.filter(id__in=to_delete).delete()

            # Update or create contacts
            for contact_data in contacts_data:
                contact_id = contact_data.get("id")
                if contact_id and contact_id in existing_contacts:
                    # Update existing
                    print("updated contact")
                    for attr, value in contact_data.items():
                        setattr(existing_contacts[contact_id], attr, value)
                    existing_contacts[contact_id].save()
                else:
                    print("created new contact")
                    FestivalContact.objects.create(festival=instance, **contact_data)

        return instance

    def get_current_year_application(self, obj: Festival) -> dict[str, Any]:
        # application_year = request.application_year
        # Calculate date range for this year
        from datetime import date
        from django.contrib.contenttypes.models import ContentType
        from applications.models import Application
        from applications.serializer import MinimalApplicationSerializer

        year_start = date(2026 - 1, 9, 1)
        year_end = date(2026, 8, 31)

        # Get applications for this specific festival using GenericForeignKey
        festival_content_type = ContentType.objects.get_for_model(Festival)
        application = Application.objects.filter(
            content_type=festival_content_type,
            object_id=obj.pk,
            application_date__gte=year_start,
            application_date__lte=year_end,
        ).first()

        return MinimalApplicationSerializer(application, context=self.context).data

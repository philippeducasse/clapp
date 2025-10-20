from datetime import datetime
from typing import Any, Dict
from django.db.models import Exists, OuterRef, Subquery, QuerySet
from django.core.mail import EmailMultiAlternatives
from django.utils import timezone
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.utils.html import strip_tags
from django.contrib.contenttypes.models import ContentType
from organisations.festivals.models import Festival
from organisations.festivals.serializer import FestivalSerializer
from applications.models import Application
from services.gemini_service import GeminiClient
from .utils import (
    generate_application_mail_prompt,
    extract_fields_from_llm,
    clean_festival_data,
    generate_enrich_prompt,
)
from services.mistral_service import MistralClient
from django.http import HttpRequest
from performances.models import Performance
from profiles.models import Profile
from django_filters.rest_framework import DjangoFilterBackend


# Provides CRUD operations for Festival
class FestivalViewSet(viewsets.ModelViewSet):
    # Class used to convert JSON into Django Model objects and vice versa
    serializer_class = FestivalSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["country", "festival_type"]
    search_fields = ["name"]
    ordering_fields = ["name", "start_date", "application_date_start"]
    ordering = ["name"]

    def get_queryset(self) -> QuerySet[Festival]:
        # annotates all festival objects
        festival_content_type = ContentType.objects.get_for_model(Festival)
        queryset = Festival.objects.annotate(
            has_application_this_year=Exists(
                Application.objects.filter(
                    content_type=festival_content_type,
                    object_id=OuterRef("pk"),
                    application_date__year=2026,
                )
            ),
            latest_application_status=Subquery(
                Application.objects.filter(
                    content_type=festival_content_type, object_id=OuterRef("pk")
                )
                .order_by("-application_date")
                .values("application_status")[:1]
            ),
            latest_application_date=Subquery(
                Application.objects.filter(
                    content_type=festival_content_type, object_id=OuterRef("pk")
                )
                .order_by("-application_date")
                .values("application_date")[:1]
            ),
        )
        return queryset

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.mistral_client = MistralClient()
        self.gemini_client = GeminiClient()

    # Adds an endpoint to default queryset. Detail means it affects only one entity
    @action(detail=True, methods=["get"])
    def enrich(self, request: HttpRequest, pk: int | None = None) -> Response:
        # Retrieves the Festival instance corresponding to the given pk (primary key) from the URL.
        festival: Festival = self.get_object()
        query = f"{festival.website_url} {festival.name} {festival.country} {datetime.now().year}"

        search_results = self.gemini_client.search(query=query)

        prompt: str = generate_enrich_prompt(festival, search_results)
        llm_response: str = self.mistral_client.chat(prompt=prompt)
        print("RESPONSE", llm_response)

        updated_fields: Dict[str, Any] = extract_fields_from_llm(llm_response)

        # Update the fields with LLM-provided values (including contacts)
        for field, value in updated_fields.items():
            if field not in [
                "sources",
                "updated_fields",
                "contacts",
            ]:  # Skip meta fields & contact field
                setattr(festival, field, value)

        clean_festival_data(festival)
        enriched_data = FestivalSerializer(festival).data

        if "contacts" in updated_fields:
            enriched_data["contacts"] = updated_fields["contacts"]

        return Response(enriched_data)

    @action(detail=True, methods=["post"])
    def apply(self, request: HttpRequest, pk: int) -> Response:
        try:
            festival = Festival.objects.get(pk=pk)
        except Festival.DoesNotExist:
            return Response(
                {"error": "Festival not found"}, status=status.HTTP_400_BAD_REQUEST
            )

        try:
            message = request.data.get("message")
            subject = request.data.get("email_subject")
            attachments = request.FILES.getlist("attachments_sent")
            performances = request.data.get("performances")
            if not message or not subject:
                return Response(
                    {"error": "Message and/or subject not found"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Calculate the application year
            current_date = timezone.now().date()
            application_year = current_date.year
            if current_date.month >= 9:
                application_year += 1

            # Check if an application already exists for the festival and year
            festival_content_type = ContentType.objects.get_for_model(Festival)
            applications = Application.objects.filter(
                content_type=festival_content_type, object_id=festival.pk
            )
            existing_application = next(
                (a for a in applications if a.application_year == application_year),
                None,
            )

            if existing_application:
                return Response(
                    "Application already exists for this festival and year",
                    status=status.HTTP_400_BAD_REQUEST,
                )
            default_profile = Profile.objects.get(id=2)
            application = Application.objects.create(
                organisation=festival,
                application_date=timezone.now().date(),
                application_status="DRAFT",
                message=message,
                email_subject=subject,
                profile=default_profile,
            )

            if performances:
                performance_objects = Performance.objects.filter(
                    id__in=performances.split(",")
                )
                application.performances.set(performance_objects)
                for p in performance_objects:
                    for dossier in p.dossiers.all():
                        print("attaching")
                        attachments.append(dossier.file)

            if attachments:
                application.attachments_sent = [file.name for file in attachments]
                application.save()

            try:
                text_content = strip_tags(application.message)  # plain text fallback
                html_content = application.message  # Tiptap HTML

                # Get all contact emails from the festival
                recipient_emails = [
                    contact.email for contact in festival.contacts.all()
                ]
                if not recipient_emails:
                    return Response(
                        {"error": "No contact emails found for this festival"},
                        status=status.HTTP_400_BAD_REQUEST,
                    )

                email = EmailMultiAlternatives(
                    subject,
                    text_content,
                    "info@philippeducasse.com",
                    recipient_emails,
                    # ["ducassephi@hotmail.fr"],
                    bcc=["info@philippeducasse.com"],
                )
                email.attach_alternative(html_content, "text/html")

                if performances:
                    for p in performance_objects:
                        if p.dossiers:
                            for dossier in p.dossiers.all():
                                print("attaching 2")
                                attachments.append(dossier.file)
                                filename = dossier.file.name.split("/")[-1]
                                # Open and attach the file from storage
                                email.attach(
                                    filename,
                                    dossier.file.read(),
                                    "application/pdf",
                                )

                for file in attachments:
                    print("file:", file)
                    if hasattr(file, "content_type"):
                        # It's an uploaded file from request.FILES
                        email.attach(file.name, file.read(), file.content_type)

                email.send(fail_silently=False)
                application.application_status = "APPLIED"
                application.save()
                return Response(
                    {"message": "Application sent successfully"}, status=200
                )
            except Exception as e:
                return Response(
                    {"error": f"Email failed to send: {str(e)}"}, status=500
                )

        except Exception as e:
            return Response(
                {
                    "error": "Failed to process application",
                    "details": str(e),
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @action(detail=True, methods=["post"])
    def generate_email(self, request: HttpRequest, pk: int) -> Response:
        try:
            festival = Festival.objects.get(pk=pk)
            profile = Profile.objects.get(
                id=2
            )  # TODO: Use request.user.profile in production

            performance_ids = request.data.get("selected_performance_ids")

            # performances = data.performances
            performance_objects = []

            # Parse performance IDs and fetch objects if provided
            if performance_ids:
                if isinstance(performance_ids, str):
                    performance_ids = [
                        int(id.strip())
                        for id in performance_ids.split(",")
                        if id.strip()
                    ]
                elif isinstance(performance_ids, list):
                    performance_ids = performance_ids
                else:
                    performance_ids = [performance_ids]

                performance_objects = list(
                    Performance.objects.filter(id__in=performance_ids)
                )

                if not performance_objects:
                    pass

            # Generate email content (works with empty list too)
            prompt = generate_application_mail_prompt(
                festival, profile, performance_objects
            )
            message = self.mistral_client.chat(prompt=prompt)

            return Response({"message": message}, status=status.HTTP_200_OK)

        except Festival.DoesNotExist:
            return Response(
                {"error": "Festival not found"}, status=status.HTTP_404_NOT_FOUND
            )
        except Profile.DoesNotExist:
            return Response(
                {"error": "Profile not found"}, status=status.HTTP_404_NOT_FOUND
            )
        except ValueError as e:
            return Response(
                {"error": f"Invalid performance ID format: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Exception as e:
            return Response(
                {"error": f"Failed to generate email: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

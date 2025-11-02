from datetime import datetime
from typing import Any, Dict, List
from django.core.mail import EmailMultiAlternatives
from django.utils import timezone
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework.decorators import action, api_view, permission_classes
from django.utils.html import strip_tags
from django.contrib.contenttypes.models import ContentType
from django.http import HttpRequest
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.db.models import Q
from organisations.festivals.models import Festival
from organisations.residencies.models import Residency
from organisations.venues.models import Venue
from applications.models import Application
from services.gemini_service import GeminiClient
from services.mistral_service import MistralClient
from performances.models import Performance
from profiles.models import Profile
from .models import Organisation
from .utils import (
    generate_application_mail_prompt,
    extract_fields_from_llm,
    clean_organisation_data,
    generate_enrich_prompt,
)


@api_view(["GET"])
# todo: add authentication?
# @permission_classes([])
def search(request: Request) -> Response:
    """
    Unified search endpoint for all organisation types
    GET /api/organisations/search/?q=search_term
    Returns array of organizations matching search query
    """
    search_query = request.query_params.get("q", "")

    if len(search_query) < 2:
        return Response([], status=200)

    search_filter = (
        Q(name__icontains=search_query)
        | Q(website_url__icontains=search_query)
        | Q(description__icontains=search_query)
    )

    festivals = Festival.objects.filter(search_filter).values(
        "id", "name", "country", "town"
    )[:20]
    venues = Venue.objects.filter(search_filter).values(
        "id", "name", "country", "town"
    )[:20]
    residencies = Residency.objects.filter(search_filter).values(
        "id", "name", "country", "town"
    )[:20]

    results: List[Dict[str, Any]] = []

    for festival in festivals:
        results.append({**festival, "type": "festival"})

    for venue in venues:
        results.append({**venue, "type": "venue"})

    for residency in residencies:
        results.append({**residency, "type": "residency"})

    results.sort(key=lambda x: x["name"].lower())

    results = results[:15]

    return Response(results, status=200)


class OrganisationViewSet(viewsets.ModelViewSet):
    """
    Base ViewSet for all organisation types (festivals, venues, residencies).
    Provides shared functionality like enrich, apply, and generate_email.
    """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self._mistral_client = None
        self._gemini_client = None

    @property
    def mistral_client(self) -> MistralClient:
        if self._mistral_client is None:
            self._mistral_client = MistralClient()
        return self._mistral_client

    @property
    def gemini_client(self) -> GeminiClient:
        if self._gemini_client is None:
            self._gemini_client = GeminiClient()
        return self._gemini_client

    def get_organisation_type_name(self) -> str:
        """
        Override in subclasses to return the organisation type name.
        Used for search queries and prompts.
        """
        return "organisation"

    def get_enrich_prompt(self, organisation: Organisation, search_results: str) -> str:
        """
        Generate enrichment prompt for the organisation.
        Override in subclasses to provide type-specific prompts.
        """
        return generate_enrich_prompt(organisation, search_results)

    @action(detail=True, methods=["get"])
    def enrich(self, request: HttpRequest, pk: int | None = None) -> Response:
        """Enrich organisation data using LLM and web search."""
        organisation: Organisation = self.get_object()
        org_type = self.get_organisation_type_name()

        query = f"{organisation.website_url} {organisation.name} {organisation.country} {datetime.now().year} {org_type}"
        search_results = self.gemini_client.search(query=query)

        prompt: str = self.get_enrich_prompt(organisation, search_results)
        print("prompt: ", prompt)
        llm_response: str = self.mistral_client.chat(prompt=prompt)
        print("RESPONSE", llm_response)

        updated_fields: Dict[str, Any] = extract_fields_from_llm(llm_response)

        # Update the fields with LLM-provided values (including contacts)
        for field, value in updated_fields.items():
            if field not in ["sources", "updated_fields", "contacts"]:
                setattr(organisation, field, value)

        clean_organisation_data(organisation)
        enriched_data = self.get_serializer(organisation).data

        if "contacts" in updated_fields:
            enriched_data["contacts"] = updated_fields["contacts"]

        return Response(enriched_data)

    @action(detail=True, methods=["post"])
    def apply(self, request: HttpRequest, pk: int) -> Response:
        """Submit an application to the organisation."""
        try:
            organisation = self.get_object()
        except self.queryset.model.DoesNotExist:
            return Response(
                {
                    "error": f"{self.get_organisation_type_name().capitalize()} not found"
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        # Parse and validate recipients
        recipients_input = request.data.get("recipients", "")
        recipient_emails = [
            email.strip() for email in recipients_input.split(",") if email.strip()
        ]

        if not recipient_emails:
            return Response(
                {"error": "At least one recipient email is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Validate email format
        try:
            for email in recipient_emails:
                validate_email(email)
        except ValidationError:
            return Response(
                {"error": "Invalid email address format"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Get message and subject
        message = request.data.get("message")
        subject = request.data.get("email_subject")

        if not message or not subject:
            return Response(
                {"error": "Message and/or subject not found"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        attachments = request.FILES.getlist("attachments_sent")
        performances = request.data.get("performances")

        # Calculate application year
        current_date = timezone.now().date()
        application_year = current_date.year
        if current_date.month >= 9:
            application_year += 1

        # Get or create application
        organisation_content_type = ContentType.objects.get_for_model(
            organisation.__class__
        )
        applications = Application.objects.filter(
            content_type=organisation_content_type, object_id=organisation.pk
        )

        application = next(
            (a for a in applications if a.application_year == application_year),
            None,
        )

        if application:
            if application.application_status != "DRAFT":
                return Response(
                    "Application already exists for this organisation and year",
                    status=status.HTTP_400_BAD_REQUEST,
                )
            else:
                application.message = message
                application.email_subject = subject
                application.save()
        else:
            # TODO: refactor this once more than one user
            default_profile = Profile.objects.get(id=2)

            application = Application.objects.create(
                organisation=organisation,
                application_date=timezone.now().date(),
                application_status="DRAFT",
                message=message,
                email_subject=subject,
                profile=default_profile,
            )

        # Send email
        try:
            text_content = strip_tags(application.message)
            html_content = application.message

            email = EmailMultiAlternatives(
                subject,
                text_content,
                "info@philippeducasse.com",
                recipient_emails,
                # bcc=["info@philippeducasse.com"],
            )
            email.attach_alternative(html_content, "text/html")

            # Attach performance dossiers
            if performances:
                performance_objects = Performance.objects.filter(
                    id__in=performances.split(",")
                )
                for p in performance_objects:
                    if p.dossiers:
                        for dossier in p.dossiers.all():
                            filename = dossier.file.name.split("/")[-1]
                            email.attach(
                                filename,
                                dossier.file.read(),
                                "application/pdf",
                            )

            # Attach uploaded files
            for file in attachments:
                if hasattr(file, "content_type"):
                    email.attach(file.name, file.read(), file.content_type)

            email.send(fail_silently=False)
            application.application_status = "APPLIED"
            application.save()

            return Response(
                {
                    "message": "Application sent successfully",
                    "applicationId": application.id,
                },
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return Response(
                {"error": f"Email failed to send: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @action(detail=True, methods=["post"])
    def generate_email(self, request: HttpRequest, pk: int) -> Response:
        """Generate email content using LLM."""
        try:
            organisation = self.get_object()
            profile = Profile.objects.get(id=2)  # TODO: Use request.user.profile

            performance_ids = request.data.get("selected_performance_ids")
            performance_objects = []

            # Parse performance IDs
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

            # Generate email content
            prompt = generate_application_mail_prompt(
                organisation, profile, performance_objects
            )
            message = self.mistral_client.chat(prompt=prompt)

            return Response({"message": message}, status=status.HTTP_200_OK)

        except self.queryset.model.DoesNotExist:
            return Response(
                {
                    "error": f"{self.get_organisation_type_name().capitalize()} not found"
                },
                status=status.HTTP_404_NOT_FOUND,
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

    @action(detail=True, methods=["patch"], url_path="tag/(?P<tag_action>[^/.]+)")
    def tag(self, request: HttpRequest, pk: int, tag_action: str) -> Response:
        """Add or remove tags from organisation."""
        organisation = self.get_object()
        valid_actions = ["STAR", "WARNING", "INACTIVE", "WATCH", "IRRELEVANT", "OTHER"]

        if tag_action not in valid_actions:
            return Response(
                {
                    "error": f"Invalid action. Must be one of: {', '.join(valid_actions)}"
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        organisation.tag = "" if tag_action == organisation.tag else tag_action
        organisation.save()

        serializer = self.get_serializer(organisation)
        return Response(serializer.data)

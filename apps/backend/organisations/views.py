import logging
from datetime import datetime
from typing import Any, Dict, List

import pandas as pd
from django.apps import apps
from django.db.models import Q
from django.http import HttpRequest
from django.utils import timezone
from rest_framework import status, viewsets
from rest_framework.decorators import action, api_view
from rest_framework.request import Request
from rest_framework.response import Response

from organisations.festivals.models import Festival, FestivalContact
from organisations.residencies.models import Residency, ResidencyContact
from organisations.venues.models import Venue, VenueContact
from performances.models import Performance
from services.mistral_service import ConversationResponse, MistralClient

from .models import Organisation
from .services import (
    create_form_application,
    extract_search_results,
    generate_application_mail_prompt,
    generate_enrich_prompt,
    get_or_create_application,
    prepare_application_email,
    send_application_email,
    validate_application_recipients,
)
from .utils import clean_organisation_data, extract_fields_from_llm, normalize_domain

logger = logging.getLogger(__name__)


@api_view(["GET"])
def search(request: Request) -> Response:
    """
    Unified search endpoint for all organisation types
    GET /api/organisations/search/?q=search_term
    Returns array of organizations matching search query
    """
    ORGANISATION_SEARCH_FIELDS = ["id", "name", "country", "town"]

    search_query = request.query_params.get("q", "")
    organisation_type = request.query_params.get("type", None)

    if len(search_query) < 2:
        return Response([], status=200)

    search_filter = (
        Q(name__icontains=search_query)
        | Q(website_url__icontains=search_query)
        | Q(description__icontains=search_query)
    )

    if organisation_type:
        MODEL_MAP = {
            "festival": ("festivals", "Festival"),
            "residency": ("residencies", "Residency"),
            "venue": ("venues", "Venue"),
        }
        model_info = MODEL_MAP.get(organisation_type)
        if not model_info:
            return Response({"error": "Invalid organisation type"}, status=400)

        app_label, model_name = model_info

        try:
            Entity = apps.get_model(app_label, model_name)
            results = Entity.objects.filter(search_filter, user=request.user).values(
                *ORGANISATION_SEARCH_FIELDS
            )[:20]
        except LookupError:
            return Response({"error": "Model not found"}, status=400)

    else:
        festivals = Festival.objects.filter(search_filter, user=request.user).values(
            *ORGANISATION_SEARCH_FIELDS
        )[:20]
        venues = Venue.objects.filter(search_filter, user=request.user).values(
            *ORGANISATION_SEARCH_FIELDS
        )[:20]
        residencies = Residency.objects.filter(search_filter, user=request.user).values(
            *ORGANISATION_SEARCH_FIELDS
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

    @property
    def mistral_client(self) -> MistralClient:
        if self._mistral_client is None:
            self._mistral_client = MistralClient()
        return self._mistral_client

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

    def perform_create(self, serializer):
        instance = serializer.save(user=self.request.user)
        instance.full_clean()
        instance.save()

    def perform_update(self, serializer):
        instance = serializer.save()
        instance.full_clean()
        instance.save()

    # instance.delete() has ben overriding in organisation.views() to soft delete
    def perform_destroy(self, instance):
        """Override to use soft delete"""
        logger.info("Performing destroy")
        instance.delete()

    @action(detail=True, methods=["post"])
    def restore(self, request: HttpRequest, pk: int) -> Response:
        """Restore a soft-deleted organisation"""
        # Get the model class from the serializer
        model_class = self.get_serializer_class().Meta.model

        try:
            organisation = model_class.objects.with_deleted().filter(user=request.user).get(pk=pk)

            if organisation.deleted_at is None:
                return Response(
                    {"error": "Organisation is not deleted"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            organisation.restore()
            serializer = self.get_serializer(organisation)

            return Response(
                {
                    "message": f"{self.get_organisation_type_name().capitalize()} restored successfully",
                    "data": serializer.data,
                },
                status=status.HTTP_200_OK,
            )
        except model_class.DoesNotExist:
            return Response(
                {"error": f"{self.get_organisation_type_name().capitalize()} not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

    @action(detail=True, methods=["get"])
    def enrich(self, request: HttpRequest, pk: int | None = None) -> Response:
        """Enrich organisation data using LLM and web search."""
        organisation: Organisation = self.get_object()
        org_type = self.get_organisation_type_name()

        query = f"{organisation.website_url} {organisation.name} {organisation.country} {datetime.now().year} {org_type}"
        # search_results = self.gemini_client.search(query, request.user.id)

        search_results: ConversationResponse = self.mistral_client.search(query=query)
        parsed_results: str = extract_search_results(search_results)

        logger.info("SEARCH: %s", search_results)
        prompt: str = self.get_enrich_prompt(organisation, parsed_results)
        logger.info("prompt: %s", prompt)

        # TODO: after postgres migration, change to tenant_schema
        llm_response: str = self.mistral_client.chat(prompt, request.user.id)
        logger.info("RESPONSE: %s", llm_response)

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
        logger.debug(f"Processing application for organisation {pk}")
        logger.debug(f"Request data: {request.data}")
        try:
            organisation = self.get_object()
            logger.debug(f"Found organisation: {organisation.id}")
        except Exception:
            logger.error(f"Organisation {pk} not found")
            return Response(
                {"error": f"{self.get_organisation_type_name().capitalize()} not found"},
                status=status.HTTP_404_NOT_FOUND,
            )
        from organisations.services import parse_performance_ids

        profile = request.user
        application_method = request.data.get("application_method")
        performance_ids = request.data.get("performances")
        performances = parse_performance_ids(performance_ids)
        comments = request.data.get("comments", None)
        logger.debug(f"Application method: {application_method}")
        logger.debug(f"Parsed performances: {performances}")

        if application_method == "FORM":
            try:
                online_form_application = create_form_application(
                    organisation, performances, profile, comments
                )
                logger.info(
                    f"Form application created for organisation {organisation.id} by user {profile.id}"
                )
                return Response(
                    {
                        "message": "Form application created",
                        "applicationId": online_form_application.id,
                    },
                    status=status.HTTP_200_OK,
                )
            except Exception as e:
                logger.error(
                    f"Failed to create form application for organisation {organisation.id}: {str(e)}"
                )
                return Response(
                    {
                        "error": f"Failed to create form application for{self.get_organisation_type_name().capitalize()}"
                    },
                    status=status.HTTP_404_NOT_FOUND,
                )

        try:
            recipients_input = request.data.get("recipients", "")
            logger.debug(f"Validating recipients for email application {recipients_input}")
            recipient_emails = validate_application_recipients(recipients_input)
            logger.debug(f"Valid recipients: {recipient_emails}")
        except ValueError as e:
            logger.warning(f"Invalid email in application: {str(e)}")
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        message = request.data.get("message")
        subject = request.data.get("email_subject")
        if not message or not subject:
            logger.warning("Missing message or subject")
            return Response(
                {"error": "Message and/or subject not found"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        current_date = timezone.now().date()
        application_year = current_date.year
        if current_date.month >= 9:
            application_year += 1

        logger.debug(f"Creating/updating application for year {application_year}")
        try:
            application = get_or_create_application(
                organisation,
                profile,
                performances,
                application_year,
                message,
                subject,
                recipient_emails,
            )
            logger.debug(f"Application created/updated: {application.id}")
        except ValueError as e:
            logger.error(f"Failed to create application: {str(e)}")
            return Response(str(e), status=status.HTTP_400_BAD_REQUEST)

        logger.debug("Preparing and sending email")
        try:
            dossiers = request.data.get("dossiers")
            attachments = request.FILES.getlist("attachments_sent")

            email = prepare_application_email(
                application,
                recipient_emails,
                dossiers,
                attachments,
                profile,
                performance_ids,
            )
            logger.debug("Email prepared, sending now...")
            send_application_email(email, application)
            logger.debug("Email sent successfully")

            logger.info(
                f"Application {application.id} sent successfully to {recipient_emails} for organisation {organisation.id}"
            )
            return Response(
                {
                    "message": "Application sent successfully",
                    "applicationId": application.id,
                },
                status=status.HTTP_200_OK,
            )
        except ValueError as e:
            logger.warning(f"Invalid data in application: {str(e)}")
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(
                f"Failed to send application email for organisation {organisation.id}: {str(e)}"
            )
            return Response(
                {"error": f"Email failed to send: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @action(detail=True, methods=["post"])
    def generate_email(self, request: HttpRequest, pk: int) -> Response:
        """Generate email content using LLM."""
        from django.http import Http404

        try:
            organisation = self.get_object()
        except Http404:
            return Response(
                {"error": f"{self.get_organisation_type_name().capitalize()} not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        try:
            profile = request.user

            performance_ids = request.data.get("selected_performance_ids")
            performance_objects = []

            if performance_ids:
                if isinstance(performance_ids, str):
                    performance_ids = [
                        int(id.strip()) for id in performance_ids.split(",") if id.strip()
                    ]
                elif isinstance(performance_ids, list):
                    performance_ids = performance_ids
                else:
                    performance_ids = [performance_ids]

                performance_objects = list(Performance.objects.filter(id__in=performance_ids))

            language = request.data.get("language", "ENGLISH")
            email_length = request.data.get("message_length", None)

            prompt = generate_application_mail_prompt(
                organisation, profile, performance_objects, language, email_length
            )
            # TODO: after postgres migration, change to tenant_schema
            message = self.mistral_client.chat(prompt, request.user.id)

            return Response({"message": message}, status=status.HTTP_200_OK)

        except ValueError as e:
            return Response(
                {"error": f"Invalid performance ID format: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Exception as e:
            logger.error(f"Error generating email: {str(e)}", exc_info=True)
            return Response(
                {"error": f"Error generating email: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @action(detail=True, methods=["patch"], url_path="tag/(?P<tag_action>[^/.]+)")
    def tag(self, request: HttpRequest, pk: int, tag_action: str) -> Response:
        """Add or remove tags from organisation."""
        organisation = self.get_object()
        valid_actions = ["STAR", "WARNING", "INACTIVE", "WATCH", "IRRELEVANT", "OTHER"]

        if tag_action not in valid_actions:
            return Response(
                {"error": f"Invalid action. Must be one of: {', '.join(valid_actions)}"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        organisation.tag = "" if tag_action == organisation.tag else tag_action
        organisation.save()

        serializer = self.get_serializer(organisation)
        return Response(serializer.data)

    @action(detail=False, methods=["post"], url_path="upload")
    def upload(self, request: HttpRequest) -> Response:
        """Import organisations from Excel file."""
        excel_file = request.data.get("excel")

        if not excel_file:
            logger.warning("Upload called without excel file")
            return Response(
                {"error": "No Excel file provided"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            df: pd.DataFrame = pd.read_excel(excel_file, dtype=str)
        except Exception as e:
            logger.error(f"Failed to read Excel file: {str(e)}")
            return Response(
                {"error": f"Invalid Excel file: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        stats = {
            "festivals_imported": 0,
            "festivals_skipped": 0,
            "residencies_imported": 0,
            "residencies_skipped": 0,
            "venues_imported": 0,
            "venues_skipped": 0,
            "errors": [],
        }

        type_config = {
            "festival": {
                "model": Festival,
                "contact_model": FestivalContact,
                "contact_fk": "festival",
                "stats_key": "festivals",
            },
            "residency": {
                "model": Residency,
                "contact_model": ResidencyContact,
                "contact_fk": "residency",
                "stats_key": "residencies",
            },
            "venue": {
                "model": Venue,
                "contact_model": VenueContact,
                "contact_fk": "venue",
                "stats_key": "venues",
            },
        }

        def get_cell(row_dict: Dict[str, str], key: str, default: str = "") -> str:
            """Get value from row dict with case-insensitive key lookup."""
            key_lower = key.lower()
            for k, v in row_dict.items():
                if k.lower() == key_lower:
                    return str(v or "").strip()
            return default

        def domain_exists(model_class, website: str, index: int) -> bool:
            if not website:
                return False
            normalized_domain = normalize_domain(website)
            if model_class.objects.filter(
                website_url__icontains=normalized_domain, user=request.user
            ).exists():
                logger.info(
                    f"Row {index}: {model_class._meta.object_name} with domain '{normalized_domain}' already exists"
                )
                return True
            return False

        def resolve_org_type(name: str, organisation_type: str) -> str | None:
            if "festival" in name or organisation_type == "festival":
                return "festival"
            if "residenc" in name or "residenc" in organisation_type:
                return "residency"
            if organisation_type == "venue":
                return "venue"
            return None

        try:
            for index, row in df.iterrows():
                try:
                    row_dict = {k.lower(): v for k, v in row.to_dict().items()}

                    name = get_cell(row_dict, "name").lower()
                    organisation_type = get_cell(
                        row_dict, "type", get_cell(row_dict, "event_type")
                    ).lower()

                    if not name:
                        continue

                    resolved_type = resolve_org_type(name, organisation_type)
                    if not resolved_type:
                        error_msg = f"Row {index}: Invalid organisation type: {organisation_type}"
                        logger.error(error_msg)
                        stats["errors"].append(error_msg)
                        continue

                    config = type_config[resolved_type]
                    model_class = config["model"]
                    stats_key = config["stats_key"]

                    contact_email = get_cell(row_dict, "email")
                    contact_person = get_cell(row_dict, "contact")
                    country = get_cell(row_dict, "country")
                    website = get_cell(row_dict, "website")
                    date_str = get_cell(row_dict, "date")
                    comments = get_cell(row_dict, "comments")

                    if model_class.objects.filter(name__iexact=name, user=request.user).exists():
                        logger.info(f"Row {index}: {resolved_type} '{name}' already exists")
                        stats[f"{stats_key}_skipped"] += 1
                        continue

                    if domain_exists(model_class, website, index):
                        stats[f"{stats_key}_skipped"] += 1
                        continue

                    fields = {
                        "name": name,
                        "country": country,
                        "website_url": website,
                        "comments": comments,
                        "user": request.user,
                    }
                    if model_class != Venue:
                        fields["approximate_date"] = date_str

                    org = model_class(**fields)
                    org.save()

                    if contact_email:
                        config["contact_model"].objects.create(
                            name=contact_person,
                            email=contact_email,
                            user=request.user,
                            **{config["contact_fk"]: org},
                        )

                    logger.info(f"Imported {resolved_type}: {org.name}")
                    stats[f"{stats_key}_imported"] += 1

                except Exception as e:
                    error_msg = f"Row {index}: {str(e)}"
                    logger.error(error_msg)
                    stats["errors"].append(error_msg)

            logger.info(
                f"Upload completed: {stats['festivals_imported']} festivals, "
                f"{stats['residencies_imported']} residencies, {stats['venues_imported']} venues"
            )
            return Response(stats, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"Unexpected error during upload: {str(e)}", exc_info=True)
            return Response(
                {"error": f"Upload failed: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

from typing import Optional

from django.contrib.contenttypes.models import ContentType
from django.db.models import Exists, OuterRef, QuerySet, Subquery
from django_filters.rest_framework import DjangoFilterBackend

from applications.models import Application
from organisations.festivals.models import Festival
from organisations.festivals.serializer import FestivalSerializer
from organisations.models import Organisation
from organisations.services import (
    generate_enrich_prompt as generate_festival_enrich_prompt,
)
from organisations.views import OrganisationViewSet


class FestivalViewSet(OrganisationViewSet):
    serializer_class = FestivalSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["country", "festival_type"]
    search_fields = ["name"]
    ordering_fields = ["name", "start_date", "application_date_start"]
    ordering = ["name"]

    def get_queryset(self) -> QuerySet[Festival]:
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

    def get_organisation_type_name(self) -> str:
        return "festival"

    def get_enrich_prompt(
        self, organisation: Organisation, search_results: Optional[str]
    ) -> str:
        """Use festival-specific enrichment prompt."""
        return generate_festival_enrich_prompt(organisation, search_results)

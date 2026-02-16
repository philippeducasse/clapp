from datetime import date
from typing import Optional

from django.contrib.contenttypes.models import ContentType
from django.db.models import Exists, OuterRef, Prefetch, QuerySet
from django_filters.rest_framework import DjangoFilterBackend

from applications.models import Application
from organisations.festivals.models import Festival
from organisations.festivals.serializer import FestivalSerializer
from organisations.festivals.utils import generate_enrich_prompt as generate_festival_enrich_prompt
from organisations.models import Organisation
from organisations.views import OrganisationViewSet


class FestivalViewSet(OrganisationViewSet):
    serializer_class = FestivalSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["country", "festival_type"]
    search_fields = ["name"]
    ordering_fields = ["name", "start_date", "application_date_start"]
    ordering = ["name"]

    def get_queryset(self) -> QuerySet[Festival]:
        include_deleted = (
            self.request.query_params.get("include_deleted", "false").lower() == "true"
        )

        base_queryset = (
            Festival.objects.with_deleted().filter(user=self.request.user)
            if include_deleted
            else Festival.objects.filter(user=self.request.user)
        )

        festival_content_type = ContentType.objects.get_for_model(Festival)
        year_start = date(2026 - 1, 9, 1)
        year_end = date(2026, 8, 31)
        user_profile_id = self.request.user.id
        queryset = (
            base_queryset.annotate(
                has_application_this_year=Exists(
                    Application.objects.filter(
                        content_type=festival_content_type,
                        object_id=OuterRef("pk"),
                        application_date__year=2026,
                        profile_id=user_profile_id,
                        deleted_at__isnull=True,
                    )
                ),
            )
            .prefetch_related(
                Prefetch(
                    "applications",
                    queryset=Application.objects.filter(
                        content_type=festival_content_type,
                        application_date__gte=year_start,
                        application_date__lte=year_end,
                        profile_id=user_profile_id,
                        deleted_at__isnull=True,
                    ).select_related("content_type"),
                    to_attr="_prefetched_current_year_apps",
                )
            )
            .prefetch_related("contacts")
        )

        return queryset

    def get_organisation_type_name(self) -> str:
        return "festival"

    def get_enrich_prompt(self, organisation: Organisation, search_results: Optional[str]) -> str:
        """Use festival-specific enrichment prompt."""
        return generate_festival_enrich_prompt(organisation, search_results)

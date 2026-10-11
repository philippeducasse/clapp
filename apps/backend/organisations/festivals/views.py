from typing import Optional

import django_filters
from django.db.models import QuerySet

from organisations.festivals.models import Festival
from organisations.festivals.serializer import FestivalSerializer
from organisations.festivals.utils import FestivalEnrichment
from organisations.festivals.utils import generate_enrich_prompt as generate_festival_enrich_prompt
from organisations.models import Organisation
from organisations.views import OrganisationFilter, OrganisationViewSet, filter_in_iexact


class FestivalFilter(OrganisationFilter):
    festival_type = django_filters.CharFilter(method=filter_in_iexact)

    class Meta:
        model = Festival
        fields = ["country", "festival_type"]


class FestivalViewSet(OrganisationViewSet):
    serializer_class = FestivalSerializer
    enrich_fields = (
        "country",
        "town",
        "website_url",
        "description",
        "comments",
        "festival_type",
        "approximate_date",
        "estimated_start_date",
        "start_date",
        "end_date",
        "application_date_start",
        "application_date_end",
        "application_type",
    )
    enrich_response_format = FestivalEnrichment
    filterset_class = FestivalFilter
    search_fields = ["name", "country", "website_url", "festival_type"]
    ordering_fields = ["name", "start_date", "application_date_start"]
    ordering = ["name"]

    def get_queryset(self) -> QuerySet[Festival]:
        return self.with_current_year_applications(super().get_queryset()).prefetch_related(
            "contacts"
        )

    def get_organisation_type_name(self) -> str:
        return "festival"

    def get_enrich_prompt(self, organisation: Organisation, search_results: Optional[str]) -> str:
        """Use festival-specific enrichment prompt."""
        return generate_festival_enrich_prompt(organisation, search_results)

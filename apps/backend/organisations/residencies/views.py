from typing import Optional

import django_filters

from organisations.residencies.models import Residency
from organisations.residencies.serializer import ResidencySerializer
from organisations.views import OrganisationFilter, OrganisationViewSet, filter_in_iexact
from organisations.residencies.utils import ResidencyEnrichment, generate_enrich_prompt
from organisations.models import Organisation


class ResidencyFilter(OrganisationFilter):
    application_type = django_filters.CharFilter(method=filter_in_iexact)

    class Meta:
        model = Residency
        fields = ["country", "application_type"]


class ResidencyViewSet(OrganisationViewSet):
    serializer_class = ResidencySerializer
    enrich_fields = (
        "country",
        "town",
        "website_url",
        "description",
        "comments",
        "approximate_date",
        "start_date",
        "end_date",
        "application_date_start",
        "application_date_end",
        "application_type",
    )
    enrich_response_format = ResidencyEnrichment
    filterset_class = ResidencyFilter
    search_fields = ["name", "country", "website_url"]
    ordering_fields = ["name", "start_date", "application_date_start"]
    ordering = ["name"]

    def get_organisation_type_name(self) -> str:
        return "residency"

    def get_enrich_prompt(self, organisation: Organisation, search_results: Optional[str]) -> str:
        """Use residency-specific enrichment prompt."""
        return generate_enrich_prompt(organisation, search_results)

from typing import Optional

import django_filters

from organisations.venues.models import Venue
from organisations.venues.serializer import VenueSerializer
from organisations.views import OrganisationFilter, OrganisationViewSet, filter_in_iexact
from organisations.venues.utils import VenueEnrichment, generate_enrich_prompt
from organisations.models import Organisation


class VenueFilter(OrganisationFilter):
    venue_type = django_filters.CharFilter(method=filter_in_iexact)

    class Meta:
        model = Venue
        fields = ["country", "venue_type"]


class VenueViewSet(OrganisationViewSet):
    serializer_class = VenueSerializer
    enrich_fields = (
        "country",
        "town",
        "website_url",
        "description",
        "comments",
        "venue_type",
    )
    enrich_response_format = VenueEnrichment
    filterset_class = VenueFilter
    search_fields = ["name", "country", "website_url"]
    ordering_fields = ["name"]
    ordering = ["name"]

    def get_organisation_type_name(self) -> str:
        return "venue"

    def get_enrich_prompt(self, organisation: Organisation, search_results: Optional[str]) -> str:
        """Use venue-specific enrichment prompt."""
        return generate_enrich_prompt(organisation, search_results)

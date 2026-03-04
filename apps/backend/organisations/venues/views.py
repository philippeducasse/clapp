from typing import Optional

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter, SearchFilter

from organisations.venues.models import Venue
from organisations.venues.serializer import VenueSerializer
from organisations.views import OrganisationViewSet
from organisations.venues.utils import generate_enrich_prompt
from organisations.models import Organisation


class VenueViewSet(OrganisationViewSet):
    serializer_class = VenueSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["country", "venue_type"]
    search_fields = ["name", "country", "website_url"]
    ordering_fields = ["name"]
    ordering = ["name"]


    def get_organisation_type_name(self) -> str:
        return "venue"

    def get_enrich_prompt(self, organisation: Organisation, search_results: Optional[str]) -> str:
        """Use venue-specific enrichment prompt."""
        return generate_enrich_prompt(organisation, search_results)

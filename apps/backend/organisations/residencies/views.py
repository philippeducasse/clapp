from typing import Optional

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter, SearchFilter

from organisations.residencies.models import Residency
from organisations.residencies.serializer import ResidencySerializer
from organisations.views import OrganisationViewSet
from organisations.residencies.utils import generate_enrich_prompt
from organisations.models import Organisation


class ResidencyViewSet(OrganisationViewSet):
    serializer_class = ResidencySerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["country", "application_type"]
    search_fields = ["name", "country", "website_url"]
    ordering_fields = ["name", "start_date", "application_date_start"]
    ordering = ["name"]


    def get_organisation_type_name(self) -> str:
        return "residency"

    def get_enrich_prompt(self, organisation: Organisation, search_results: Optional[str]) -> str:
        """Use residency-specific enrichment prompt."""
        return generate_enrich_prompt(organisation, search_results)

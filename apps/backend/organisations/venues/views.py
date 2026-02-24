from typing import Optional

from django.db.models import Q, QuerySet
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

    def get_queryset(self) -> QuerySet[Venue]:
        include_deleted = (
            self.request.query_params.get("include_deleted", "false").lower() == "true"
        )

        if self.request.user.is_staff:
            visibility_filter = (
                Q(user__isnull=True) | Q(is_seed_clone=False) | Q(user=self.request.user)
            )
        else:
            visibility_filter = Q(user=self.request.user)

        if include_deleted:
            return Venue.objects.with_deleted().filter(visibility_filter).distinct()
        else:
            return Venue.objects.filter(visibility_filter).distinct()

    def get_organisation_type_name(self) -> str:
        return "venue"

    def get_enrich_prompt(self, organisation: Organisation, search_results: Optional[str]) -> str:
        """Use venue-specific enrichment prompt."""
        return generate_enrich_prompt(organisation, search_results)

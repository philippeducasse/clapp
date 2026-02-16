from typing import Optional

from django.db.models import QuerySet

from organisations.venues.models import Venue
from organisations.venues.serializer import VenueSerializer
from organisations.views import OrganisationViewSet
from organisations.venues.utils import generate_enrich_prompt
from organisations.models import Organisation


class VenueViewSet(OrganisationViewSet):
    serializer_class = VenueSerializer

    def get_queryset(self) -> QuerySet[Venue]:
        include_deleted = (
            self.request.query_params.get("include_deleted", "false").lower() == "true"
        )

        if include_deleted:
            return Venue.objects.with_deleted().filter(user=self.request.user)
        else:
            return Venue.objects.filter(user=self.request.user)

    def get_organisation_type_name(self) -> str:
        return "venue"

    def get_enrich_prompt(self, organisation: Organisation, search_results: Optional[str]) -> str:
        """Use venue-specific enrichment prompt."""
        return generate_enrich_prompt(organisation, search_results)

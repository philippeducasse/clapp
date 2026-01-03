from django.db.models import QuerySet

from organisations.venues.models import Venue
from organisations.venues.serializer import VenueSerializer
from organisations.views import OrganisationViewSet


class VenueViewSet(OrganisationViewSet):
    serializer_class = VenueSerializer

    def get_queryset(self) -> QuerySet[Venue]:
        include_deleted = (
            self.request.query_params.get("include_deleted", "false").lower() == "true"
        )

        if include_deleted:
            return Venue.objects.with_deleted()
        else:
            return Venue.objects.all()

    def get_organisation_type_name(self) -> str:
        return "venue"

from organisations.venues.models import Venue
from organisations.venues.serializer import VenueSerializer
from organisations.views import OrganisationViewSet


class VenueViewSet(OrganisationViewSet):
    queryset = Venue.objects.all()
    serializer_class = VenueSerializer

    def get_organisation_type_name(self) -> str:
        return "venue"

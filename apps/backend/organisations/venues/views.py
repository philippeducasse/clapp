from organisations.venues.models import Venue
from organisations.venues.serializers import VenueSerializer
from rest_framework import viewsets


class VenueViewSet(viewsets.ModelViewSet):
    queryset = Venue.objects.all()
    serializer_class = VenueSerializer

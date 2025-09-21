from venues.models import Venue
from circus_agent_backend.serializers import VenueSerializer
from rest_framework import viewsets


class VenueViewSet(viewsets.ModelViewSet):
    queryset = Venue.objects.all()
    serializer_class = VenueSerializer

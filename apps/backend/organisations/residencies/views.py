from organisations.residencies.models import Residency
from organisations.residencies.serializers import ResidencySerializer
from rest_framework import viewsets


class ResidencyViewSet(viewsets.ModelViewSet):
    queryset = Residency.objects.all()
    # Class used to convert JSON into Django Model objects and vice versa
    serializer_class = ResidencySerializer

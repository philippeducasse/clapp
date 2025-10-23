from organisations.residencies.models import Residency
from organisations.residencies.serializer import ResidencySerializer
from organisations.views import OrganisationViewSet


class ResidencyViewSet(OrganisationViewSet):
    queryset = Residency.objects.all()
    serializer_class = ResidencySerializer

    def get_organisation_type_name(self) -> str:
        return "residency"

from django.db.models import QuerySet

from organisations.residencies.models import Residency
from organisations.residencies.serializer import ResidencySerializer
from organisations.views import OrganisationViewSet


class ResidencyViewSet(OrganisationViewSet):
    serializer_class = ResidencySerializer

    def get_queryset(self) -> QuerySet[Residency]:
        include_deleted = (
            self.request.query_params.get("include_deleted", "false").lower() == "true"
        )

        if include_deleted:
            return Residency.objects.with_deleted()
        else:
            return Residency.objects.all()

    def get_organisation_type_name(self) -> str:
        return "residency"

from typing import Optional

from django.db.models import Q, QuerySet

from organisations.residencies.models import Residency
from organisations.residencies.serializer import ResidencySerializer
from organisations.views import OrganisationViewSet
from organisations.residencies.utils import generate_enrich_prompt
from organisations.models import Organisation


class ResidencyViewSet(OrganisationViewSet):
    serializer_class = ResidencySerializer

    def get_queryset(self) -> QuerySet[Residency]:
        include_deleted = (
            self.request.query_params.get("include_deleted", "false").lower() == "true"
        )

        if self.request.user.is_staff:
            visibility_filter = Q(user__isnull=True) | Q(is_seed_clone=False, user__isnull=False)
        else:
            visibility_filter = Q(user=self.request.user)

        if include_deleted:
            return Residency.objects.with_deleted().filter(visibility_filter).distinct()
        else:
            return Residency.objects.filter(visibility_filter).distinct()

    def get_organisation_type_name(self) -> str:
        return "residency"

    def get_enrich_prompt(self, organisation: Organisation, search_results: Optional[str]) -> str:
        """Use residency-specific enrichment prompt."""
        return generate_enrich_prompt(organisation, search_results)

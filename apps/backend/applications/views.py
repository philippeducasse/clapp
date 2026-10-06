import django_filters
from django.db.models import QuerySet
from django.http import HttpRequest
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter
from rest_framework.response import Response

from applications.models import Application, ApplicationSeason, InboundEmail
from applications.serializer import ApplicationSerializer, InboundEmailSerializer
from applications.services import set_application_status

# Sentinel for "applications without a season". django-filter skips empty values,
# so an empty string can't be used to express this.
NO_SEASON = "__none__"


# converts URL query params into an ORM call.
class ApplicationFilter(django_filters.FilterSet):
    season = django_filters.CharFilter(method="filter_season")

    class Meta:
        model = Application
        fields = ["season"]

    def filter_season(
        self, queryset: QuerySet[Application], name: str, value: str
    ) -> QuerySet[Application]:
        if value == NO_SEASON:
            return queryset.filter(season__isnull=True)
        return queryset.filter(season__name=value)


class ApplicationViewSet(viewsets.ModelViewSet):
    queryset = Application.objects.all()
    serializer_class = ApplicationSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_class = ApplicationFilter

    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)

        # Get all seasons for this user
        seasons = (
            ApplicationSeason.objects.filter(profile_id=request.user.id)
            .values_list("name", flat=True)
            .order_by("created_at")
        )

        response.data["metadata"] = {
            "available_seasons": list(seasons),
        }
        return response

    def get_queryset(self) -> QuerySet[Application]:
        return (
            Application.objects.filter(profile_id=self.request.user.id)
            .select_related("content_type", "season")
            .prefetch_related("organisation")
        )

    @action(detail=True, methods=["patch"], url_path="status/(?P<new_status>[^/.]+)")
    def update_status(self, request: HttpRequest, pk: int, new_status: str) -> Response:
        """Update the status of an application."""
        application = self.get_object()

        set_application_status(application, new_status)

        serializer = self.get_serializer(application)
        return Response(serializer.data)


class InboundEmailViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = InboundEmailSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["state"]

    def get_queryset(self) -> QuerySet[InboundEmail]:
        return InboundEmail.objects.filter(application__profile_id=self.request.user.id)

    @action(detail=True, methods=["post"])
    def approve(self, request: HttpRequest, pk: int) -> Response:
        """Apply the suggested status, or the "status" given in the request body."""
        email = self.get_object()
        new_status = request.data.get("status") or email.suggested_status
        set_application_status(email.application, new_status, note=email.summary)
        email.state = "APPROVED"
        email.save()
        return Response(self.get_serializer(email).data)

    @action(detail=True, methods=["post"])
    def dismiss(self, request: HttpRequest, pk: int) -> Response:
        email = self.get_object()
        email.state = "DISMISSED"
        email.save()
        return Response(self.get_serializer(email).data)

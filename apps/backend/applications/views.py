from django.db.models import QuerySet
from django.http import HttpRequest
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter
from rest_framework.response import Response

from applications.models import APPLICATION_STATUS, Application, ApplicationSeason
from applications.serializer import ApplicationSerializer


class ApplicationViewSet(viewsets.ModelViewSet):
    queryset = Application.objects.all()
    serializer_class = ApplicationSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ["season"]

    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)

        # Get all seasons for this user
        seasons = (
            ApplicationSeason.objects.filter(profile_id=request.user.id)
            .values_list("year", flat=True)
            .order_by("-year")
        )

        response.data["metadata"] = {
            "available_years": list(seasons),
        }
        return response

    def get_queryset(self) -> QuerySet[Application]:
        queryset = (
            Application.objects.filter(profile_id=self.request.user.id)
            .select_related("content_type", "season")
            .prefetch_related("organisation")
        )

        # If no season filter provided, default to most recent season
        if "season" not in self.request.query_params:
            most_recent_season = (
                ApplicationSeason.objects.filter(profile_id=self.request.user.id)
                .order_by("-year")
                .first()
            )

            if most_recent_season:
                queryset = queryset.filter(season=most_recent_season)

        return queryset

    @action(detail=True, methods=["patch"], url_path="status/(?P<new_status>[^/.]+)")
    def tag(self, request: HttpRequest, pk: int, new_status: str) -> Response:
        """Add or remove tags from organisation."""
        application = self.get_object()
        valid_actions = [status[0] for status in APPLICATION_STATUS]

        if new_status not in valid_actions:
            return Response(
                {"error": f"Invalid action. Must be one of: {', '.join(valid_actions)}"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        application.status = new_status
        application.save()

        serializer = self.get_serializer(application)
        return Response(serializer.data)

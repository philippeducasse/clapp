from django.db.models import QuerySet
from django.http import HttpRequest
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from applications.models import APPLICATION_STATUS, Application
from applications.serializer import ApplicationSerializer


class ApplicationViewSet(viewsets.ModelViewSet):
    queryset = Application.objects.all()
    serializer_class = ApplicationSerializer

    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    def get_queryset(self) -> QuerySet[Application]:
        return (
            Application.objects.filter(profile_id=self.request.user.id)
            .select_related("content_type")
            .prefetch_related("organisation")
        )

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

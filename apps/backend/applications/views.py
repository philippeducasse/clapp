from django.db.models import QuerySet
from rest_framework import viewsets

from applications.models import Application
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

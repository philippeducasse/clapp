from django.db.models import QuerySet
from rest_framework import viewsets

from applications.models import Application
from applications.serializer import ApplicationSerializer


class ApplicationViewSet(viewsets.ModelViewSet):
    queryset = Application.objects.all()
    serializer_class = ApplicationSerializer

    def get_queryset(self) -> QuerySet[Application]:
        user_id = 2
        return (
            Application.objects.filter(profile_id=user_id)
            .select_related("content_type")
            .prefetch_related("organisation")
        )

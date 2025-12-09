from django.db.models import QuerySet
from rest_framework import viewsets

from applications.models import Application
from applications.serializer import ApplicationSerializer


class ApplicationViewSet(viewsets.ModelViewSet):
    queryset = Application.objects.all()
    serializer_class = ApplicationSerializer

    def list(self, request, *args, **kwargs):
        print("=" * 50)
        print("APPLICATION LIST VIEW")
        print(f"Session key: {request.session.session_key}")
        print(f"User: {request.user}")
        print(f"Is authenticated: {request.user.is_authenticated}")
        print(f"Auth: {request.auth}")
        print(f"Cookies: {request.COOKIES}")
        print(f"HTTP_COOKIE header: {request.META.get('HTTP_COOKIE', 'NOT FOUND')}")
        print(f"Origin: {request.META.get('HTTP_ORIGIN', 'NOT FOUND')}")
        print(f"Referer: {request.META.get('HTTP_REFERER', 'NOT FOUND')}")
        print("=" * 50)
        return super().list(request, *args, **kwargs)

    def get_queryset(self) -> QuerySet[Application]:
        # user_id
        print(f"GET_QUERYSET - Session key: {self.request.session.session_key}")
        print(f"GET_QUERYSET - User: {self.request.user}")
        print(f"GET_QUERYSET - Is authenticated: {self.request.user.is_authenticated}")
        return (
            Application.objects.filter(profile_id=2)
            .select_related("content_type")
            .prefetch_related("organisation")
        )

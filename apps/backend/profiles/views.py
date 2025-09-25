from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework import viewsets, status, permissions
from profiles.models import Profile
from circus_agent_backend.serializers import ProfileSerializer


class FestivalViewSet(viewsets.ModelViewSet):
    serializer_class = ProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Each user can only see their own profile
        return Profile.objects.filter(user=self.request.user)

    def get_object(self):
        # Override to ensure users can only access their own profile
        obj = super().get_object()
        if obj.user != self.request.user:
            raise permissions.exceptions.PermissionDenied(
                "You can only access your own profile"
            )
        return obj

    @action(detail=True, methods=["post"])
    def change_password(self, request) -> Response:
        profile = self.get_object()
        new_password = request.body.new_password

    @action(detail=True, methods=["get"])
    def get_profile(self) -> Response:
        profile: Profile = self.getObject()

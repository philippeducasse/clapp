from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework import viewsets, status, permissions
from profiles.models import Profile
from profiles.serializers import ProfileSerializer


class ProfileViewSet(viewsets.ModelViewSet):
    serializer_class = ProfileSerializer
    # permission_classes = [permissions.IsAuthenticated]
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        # Only return the logged-in user's profile
        return Profile.objects.filter(id=self.request.user.id)

    def get_object(self):
        obj = super().get_object()
        if obj.pk != self.request.user.pk:
            raise permissions.PermissionDenied("You can only access your own profile")
        return obj

    @action(detail=False, methods=["get"])
    def me(self, request):
        """Get the authenticated user's profile"""
        profile = self.get_queryset().first()
        serializer = self.get_serializer(profile)
        return Response(serializer.data)

    @action(detail=False, methods=["post"])
    def change_password(self, request):
        """Allow user to change their own password"""
        user = request.user
        new_password = request.data.get("new_password")

        if not new_password:
            return Response(
                {"error": "new_password required"}, status=status.HTTP_400_BAD_REQUEST
            )

        user.set_password(new_password)
        user.save()
        return Response({"status": "password changed successfully"})

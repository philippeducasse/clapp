import logging

from django.contrib.auth import authenticate
from django.contrib.auth import login as django_login
from django.contrib.auth import logout as django_logout
from django.db.models import QuerySet
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response

from profiles.models import Profile
from profiles.serializers import ProfileSerializer, RegisterSerializer

logger = logging.getLogger(__name__)


class ProfileViewSet(viewsets.ModelViewSet):
    serializer_class = ProfileSerializer

    def get_queryset(self) -> QuerySet[Profile]:
        return self.request.user

    def get_object(self) -> Profile:
        obj = super().get_object()
        if obj.pk != self.request.user.pk:
            logger.warning(
                f"User {self.request.user.pk} attempted to access profile {obj.pk}"
            )
            raise permissions.PermissionDenied("You can only access your own profile")
        return obj

    @action(detail=False, methods=["get"])
    def me(self, request: Request) -> Response:
        """Get the authenticated user's profile"""
        profile = self.get_queryset()
        serializer = self.get_serializer(profile)
        return Response(serializer.data)

    @action(detail=False, methods=["post"])
    def change_password(self, request: Request) -> Response:
        """Allow user to change their own password"""
        user = request.user
        new_password = request.data.get("new_password")

        if not new_password:
            return Response(
                {"error": "new_password required"}, status=status.HTTP_400_BAD_REQUEST
            )

        user.set_password(new_password)
        user.save()
        logger.info(f"User {user.id} changed their password")
        return Response({"status": "password changed successfully"})

    @action(detail=False, methods=["post"], permission_classes=[permissions.AllowAny])
    def register(self, request: Request) -> Response:
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            logger.info(f"New user registered: {user.email}")
            return Response(
                {"email": user.email, "message": "User created successfully"},
                status=status.HTTP_201_CREATED,
            )
        logger.warning(f"Registration failed with errors: {serializer.errors}")
        return Response(serializer.erors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=["post"], permission_classes=[permissions.AllowAny])
    def login(self, request: Request) -> Response:
        email = request.data.get("email")
        password = request.data.get("password")
        user = authenticate(request, username=email, password=password)

        if user is not None:
            django_login(request, user)
            serializer = self.get_serializer(user)
            logger.info(f"User {user.id} logged in successfully")
            return Response(serializer.data)

        logger.warning(f"Failed login attempt for email: {email}")
        return Response(
            {"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED
        )

    @action(detail=False, methods=["post"])
    def logout(self, request):
        user_id = request.user.id
        django_logout(request)
        logger.info(f"User {user_id} logged out")
        return Response({"message": "Logged out successfully"})

import logging

from django.conf import settings
from django.contrib.auth import authenticate, update_session_auth_hash
from django.contrib.auth import login as django_login
from django.contrib.auth import logout as django_logout
from django.contrib.auth.models import User
from django.db.models import QuerySet
from django.http import HttpResponseRedirect
from django.shortcuts import redirect
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.request import Request
from rest_framework.response import Response

from profiles.models import Profile, Reminder
from profiles.serializers import ProfileSerializer, RegisterSerializer, ReminderSerializer

from .tasks import send_forgot_password_email

logger = logging.getLogger(__name__)


@api_view(["GET"])
@permission_classes([permissions.AllowAny])
def confirm_email(request: Request) -> HttpResponseRedirect:
    """
    Confirm user email via token in query parameter.
    Redirects to FRONTEND_URL with status and optional error message.
    """
    token = request.GET.get("token")
    if not token:
        logger.warning(f"No valid confirmation token found! for {request}")
        return redirect(f"{settings.APP_URL}/email-confirmation?status=error&message=invalid_token")

    try:
        user = Profile.objects.get(confirmation_token=token)
        user.confirmed_account = True
        user.confirmation_token = ""
        user.save()
        logger.info(f"User {user.email} successfully confirmed")
        return redirect(f"{settings.APP_URL}/email-confirmation?status=success")
    except Profile.DoesNotExist:
        logger.warning(f"No user found found for token {token}")
        return redirect(f"{settings.APP_URL}/email-confirmation?status=error&message=invalid_token")


@api_view(["GET"])
@permission_classes([permissions.AllowAny])
def demo_login(request: Request) -> HttpResponseRedirect:
    """
    Allows users to login in directly to test account without providing credentials
    """
    TEST_USER_ID = 36

    try:
        user = User.objects.get(id=TEST_USER_ID)
    except User.DoesNotExist:
        logger.warning("Demo account not found")
        return Response({"error": "Demo account unavailable"}, status=500)

    django_login(request, user, backend="django.contrib.auth.backends.ModelBackend")
    logger.info("Test user logged in successfully")
    return Response(status.HTTP_200_OK)


@api_view(["POST"])
@permission_classes([permissions.AllowAny])
def forgot_password(request: Request) -> HttpResponseRedirect:
    """
    Confirm user email via token in query parameter.
    Redirects to FRONTEND_URL with status and optional error message.
    """
    email = request.data.get("email")
    if not email:
        logger.warning(f"No email found! for {email}")
        return Response({"error": "email required"}, status=status.HTTP_400_BAD_REQUEST)

    send_forgot_password_email.delay(email)
    return Response(status.HTTP_202_ACCEPTED)


@api_view(["POST"])
@permission_classes([permissions.AllowAny])
def reset_password(request: Request) -> HttpResponseRedirect:
    """
    Confirm user email via token in query parameter.
    Redirects to FRONTEND_URL with status and optional error message.
    """
    token = request.data.get("token")
    new_password = request.data.get("new_password")

    if not token or not new_password:
        logger.warning(f"No valid token found! for {request}")
        return Response(
            {"error": "token and new_password required"}, status=status.HTTP_400_BAD_REQUEST
        )

    try:
        user = Profile.objects.get(reset_token=token)
        user.reset_token = ""
        user.set_password(new_password)
        user.save()
        logger.info(f"User {user.email} password successfully changed")
        return Response({"message": "Password reset successfully"}, status=status.HTTP_200_OK)

    except Profile.DoesNotExist:
        logger.warning(f"No user found for token {token}")
        return Response(
            {
                "error": "User not found",
            },
            status.HTTP_404_NOT_FOUND,
        )


class ProfileViewSet(viewsets.ModelViewSet):
    serializer_class = ProfileSerializer

    def get_queryset(self) -> QuerySet[Profile]:
        # Only allow users to access their own profile
        return Profile.objects.filter(id=self.request.user.id)

    def get_object(self) -> Profile:
        obj = super().get_object()
        if obj.pk != self.request.user.pk:
            logger.warning(f"User {self.request.user.pk} attempted to access profile {obj.pk}")
            raise permissions.PermissionDenied("You can only access your own profile")
        return obj

    @action(detail=False, methods=["get"])
    def me(self, request: Request) -> Response:
        """Get the authenticated user's profile"""
        try:
            profile = request.user
            serializer = self.get_serializer(profile)
            return Response(serializer.data)
        except Exception as e:
            logger.error(f"Error fetching profile for user {request.user.pk}: {e}")
            return Response(
                {"detail": "Unable to retrieve profile."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @action(detail=False, methods=["post"])
    def change_password(self, request: Request) -> Response:
        """Allow user to change their own password"""
        user = request.user
        new_password = request.data.get("new_password")

        if not new_password:
            return Response({"error": "new_password required"}, status=status.HTTP_400_BAD_REQUEST)

        user.set_password(new_password)
        user.save()
        update_session_auth_hash(request, user)
        logger.info(f"User {user.id} changed their password")
        return Response({"message": "password changed successfully"})

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
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

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
        return Response({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)

    @action(detail=False, methods=["post"])
    def logout(self, request: Request) -> Response:
        user_id = request.user.id
        django_logout(request)
        logger.info(f"User {user_id} logged out")
        return Response({"message": "Logged out successfully"})


class ReminderViewSet(viewsets.ModelViewSet):
    serializer_class = ReminderSerializer
    pagination_class = None

    def get_queryset(self) -> QuerySet[Reminder]:
        from django.contrib.contenttypes.models import ContentType

        queryset = Reminder.objects.filter(profile=self.request.user)

        organisation_type = self.request.query_params.get("organisation_type")
        object_id = self.request.query_params.get("object_id")

        if organisation_type and object_id:
            content_type = ContentType.objects.filter(model=organisation_type.lower()).first()
            if content_type:
                queryset = queryset.filter(content_type=content_type, object_id=object_id)

        return queryset

    def perform_create(self, serializer) -> None:
        serializer.save(profile=self.request.user)

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


class ProfileViewSet(viewsets.ModelViewSet):
    serializer_class = ProfileSerializer

    def get_queryset(self) -> QuerySet[Profile]:
        print(f"Session key: {self.request.session.session_key}")
        print(f"User: {self.request.user}")
        print(f"Is authenticated: {self.request.user.is_authenticated}")
        if self.request.user.is_authenticated:
            return Profile.objects.filter(id=self.request.user.id)
        return Profile.objects.none()

    def get_object(self) -> Profile:
        obj = super().get_object()
        if obj.pk != self.request.user.pk:
            raise permissions.PermissionDenied("You can only access your own profile")
        return obj

    # def get_user(request):
    #     from django.contrib.auth.models import AnonymousUser

    #     try:
    #         user_id = request.session["sessionid"]
    #         print("SESSION_ID IN GET_USER", user_id)

    #     except KeyError:
    #         user = AnonymousUser()
    #     return user

    @action(detail=False, methods=["get"])
    def me(self, request: Request) -> Response:
        print("ME FUNCTION ############")
        print(f"Session key: {self.request.session.session_key}")
        print(f"User: {self.request.user}")
        print(f"Is authenticated: {self.request.user.is_authenticated}")
        """Get the authenticated user's profile"""
        profile = self.get_queryset().first()
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
        return Response({"status": "password changed successfully"})

    @action(detail=False, methods=["post"], permission_classes=[permissions.AllowAny])
    def register(self, request: Request) -> Response:
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response(
                {"email": user.email, "message": "User created successfully"},
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.erors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=["post"], permission_classes=[permissions.AllowAny])
    def login(self, request: Request) -> Response:
        email = request.data.get("email")
        password = request.data.get("password")
        user = authenticate(request, username=email, password=password)
        print("USER: ", password, user)

        if user is not None:
            django_login(request, user)
            serializer = self.get_serializer(user)
            print(f"Session after login: {request.session.session_key}")
            print(f"User after login: {request.user}")
            return Response(serializer.data)

        return Response(
            {"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED
        )

    @action(detail=False, methods=["post"])
    def logout(self, request):
        django_logout(request)
        return Response({"message": "Logged out successfully"})

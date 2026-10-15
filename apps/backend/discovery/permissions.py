"""Who may use discovery: superusers (frontend API) and the discovery service (internal API)."""

import hmac

from django.conf import settings
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.permissions import BasePermission


class IsSuperuser(BasePermission):
    def has_permission(self, request, view) -> bool:
        user = request.user
        return bool(user and user.is_authenticated and user.is_superuser)


class DiscoveryServiceUser:
    """Stands in for request.user when the discovery service calls the internal API."""

    is_authenticated = True
    is_superuser = False
    is_staff = False
    pk = None

    def __str__(self) -> str:
        return "discovery-service"


class ServiceTokenAuthentication(BaseAuthentication):
    """`Authorization: Bearer <DISCOVERY_SERVICE_TOKEN>`. Rejects everything if no token is configured."""

    keyword = "Bearer"

    def authenticate(self, request):
        header = request.headers.get("Authorization", "")
        if not header:
            return None  # -> 401 via authenticate_header

        keyword, _, token = header.partition(" ")
        expected = settings.DISCOVERY_SERVICE_TOKEN
        if (
            keyword != self.keyword
            or not expected
            or not hmac.compare_digest(token.strip().encode(), expected.encode())
        ):
            raise AuthenticationFailed("Invalid discovery service token.")
        return DiscoveryServiceUser(), None

    def authenticate_header(self, request) -> str:
        return self.keyword


class IsDiscoveryService(BasePermission):
    def has_permission(self, request, view) -> bool:
        return isinstance(request.user, DiscoveryServiceUser)

from django.conf import settings
from rest_framework.permissions import BasePermission


class IsNotDemoUser(BasePermission):
    def has_permission(self, request, view):
        if request.method in ["GET", "HEAD", "OPTIONS"]:
            return True
        return request.user.email != settings.DEMO_USER_EMAIL

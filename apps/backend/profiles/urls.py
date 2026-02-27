from typing import List, Union

from django.urls import URLPattern, URLResolver, include, path
from rest_framework.routers import DefaultRouter

from profiles.views import (
    ProfileViewSet,
    ReminderViewSet,
    confirm_email,
    forgot_password,
    reset_password,
)

router: DefaultRouter = DefaultRouter()
router.register(r"", ProfileViewSet, basename="profile")
router.register(r"me/reminders", ReminderViewSet, basename="reminder")
urlpatterns: List[Union[URLPattern, URLResolver]] = [
    path("confirm-email/", confirm_email, name="confirm-email"),
    path("reset-password/", reset_password, name="confirm-email"),
    path("forgot-password/", forgot_password, name="forgot-password"),
    path("", include(router.urls)),
]

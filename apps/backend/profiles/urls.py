from typing import List, Union

from django.urls import URLPattern, URLResolver, include, path
from rest_framework.routers import DefaultRouter

from profiles.oauth_views import (
    gmail_callback,
    gmail_connect,
    oauth_disconnect,
    outlook_callback,
    outlook_connect,
)
from profiles.views import (
    ProfileViewSet,
    ReminderViewSet,
    confirm_email,
    demo_login,
    forgot_password,
    reset_password,
)

router: DefaultRouter = DefaultRouter()
router.register(r"", ProfileViewSet, basename="profile")
router.register(r"me/reminders", ReminderViewSet, basename="reminder")
urlpatterns: List[Union[URLPattern, URLResolver]] = [
    path("demo-login/", demo_login, name="demo-login"),
    path("confirm-email/", confirm_email, name="confirm-email"),
    path("reset-password/", reset_password, name="confirm-email"),
    path("forgot-password/", forgot_password, name="forgot-password"),
    path("oauth/gmail/connect/", gmail_connect, name="gmail-connect"),
    path("oauth/gmail/callback/", gmail_callback, name="gmail-callback"),
    path("oauth/outlook/connect/", outlook_connect, name="outlook-connect"),
    path("oauth/outlook/callback/", outlook_callback, name="outlook-callback"),
    path("oauth/disconnect/", oauth_disconnect, name="oauth-disconnect"),
    path("", include(router.urls)),
]

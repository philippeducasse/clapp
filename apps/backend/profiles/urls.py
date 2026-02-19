from django.urls import path, include, URLPattern, URLResolver
from rest_framework.routers import DefaultRouter
from profiles.views import ProfileViewSet, ReminderViewSet, confirm_email
from typing import List, Union

router: DefaultRouter = DefaultRouter(trailing_slash=False)
router.register(r"", ProfileViewSet, basename="profile")
router.register(r"me/reminders", ReminderViewSet, basename="reminder")
urlpatterns: List[Union[URLPattern, URLResolver]] = [
    path("confirm-email", confirm_email, name="confirm-email"),
    path("", include(router.urls)),
]

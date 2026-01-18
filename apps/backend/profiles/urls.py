from django.urls import path, include, URLPattern, URLResolver
from rest_framework.routers import DefaultRouter
from profiles.views import ProfileViewSet, ReminderViewSet
from typing import List, Union

router: DefaultRouter = DefaultRouter()
router.register(r"", ProfileViewSet, basename="profile")
router.register(r"me/reminders", ReminderViewSet, basename="reminder")
urlpatterns: List[Union[URLPattern, URLResolver]] = [
    path("", include(router.urls)),
]

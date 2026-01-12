from typing import List

from django.urls import URLPattern, path
from rest_framework.routers import DefaultRouter

from .views import ReminderViewSet, search

router = DefaultRouter()
router.register(r"reminders", ReminderViewSet, basename="reminder")

urlpatterns: List[URLPattern] = [
    path("search/", search, name="organisations-search"),
] + router.urls

from django.urls import path, include, URLPattern
from rest_framework.routers import DefaultRouter
from profiles.views import ProfileViewSet
from typing import List

router: DefaultRouter = DefaultRouter()
router.register(r"", ProfileViewSet, basename="profile")
urlpatterns: List[URLPattern] = [
    path("", include(router.urls)),
]

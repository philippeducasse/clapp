from typing import List

from django.urls import URLPattern, include, path
from rest_framework.routers import DefaultRouter

from .views import OrganisationViewSet, search

router = DefaultRouter(trailing_slash=False)
router.register(r"", OrganisationViewSet, basename="organisation")

urlpatterns: List[URLPattern] = [
    path("", include(router.urls)),
    path("search", search, name="organisations-search"),
]

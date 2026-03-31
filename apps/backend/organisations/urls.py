from typing import List

from django.urls import URLPattern, include, path
from rest_framework.routers import DefaultRouter

from .views import OrganisationViewSet, search

router = DefaultRouter()
router.register(r"", OrganisationViewSet, basename="organisation")

urlpatterns: List[URLPattern] = [
    path("search/", search, name="organisations-search"),
    path("", include(router.urls)),
]

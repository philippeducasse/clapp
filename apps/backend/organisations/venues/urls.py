from typing import List

from django.urls import URLPattern, include, path
from rest_framework.routers import DefaultRouter

from organisations.venues.views import VenueViewSet

router: DefaultRouter = DefaultRouter()
router.register(r"", VenueViewSet, basename="venue")
urlpatterns: List[URLPattern] = [
    path("", include(router.urls)),
]

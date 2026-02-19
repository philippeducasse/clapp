from django.urls import path, include, URLPattern
from rest_framework.routers import DefaultRouter
from organisations.venues.views import VenueViewSet
from typing import List

router: DefaultRouter = DefaultRouter(trailing_slash=False)
router.register(r"", VenueViewSet, basename="venue")
urlpatterns: List[URLPattern] = [
    path("", include(router.urls)),
]

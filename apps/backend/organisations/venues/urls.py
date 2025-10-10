from django.urls import path, include, URLPattern
from rest_framework.routers import DefaultRouter
from venues.views import VenueViewSet
from typing import List

router: DefaultRouter = DefaultRouter()
router.register(r"", VenueViewSet, basename="venue")
urlpatterns: List[URLPattern] = [
    path("", include(router.urls)),
]

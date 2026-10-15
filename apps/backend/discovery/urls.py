"""/api/discovery/ — used by the frontend, superusers only."""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from discovery.views import DiscoveryCandidateViewSet, DiscoveryRunViewSet

router = DefaultRouter()
router.register(r"runs", DiscoveryRunViewSet, basename="discovery-run")
router.register(r"candidates", DiscoveryCandidateViewSet, basename="discovery-candidate")

urlpatterns = [path("", include(router.urls))]

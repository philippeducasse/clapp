from typing import List

from django.urls import URLPattern, include, path
from rest_framework.routers import DefaultRouter

from organisations.residencies.views import ResidencyViewSet

router: DefaultRouter = DefaultRouter()
router.register(r"", ResidencyViewSet, basename="residency")
urlpatterns: List[URLPattern] = [
    path("", include(router.urls)),
]

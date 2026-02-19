from django.urls import path, include, URLPattern
from rest_framework.routers import DefaultRouter
from organisations.residencies.views import ResidencyViewSet
from typing import List

router: DefaultRouter = DefaultRouter(trailing_slash=False)
router.register(r"", ResidencyViewSet, basename="residency")
urlpatterns: List[URLPattern] = [
    path("", include(router.urls)),
]

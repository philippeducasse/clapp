from django.urls import path, include, URLPattern
from rest_framework.routers import DefaultRouter
from residencies.views import ResidencyViewSet
from typing import List

router: DefaultRouter = DefaultRouter()
router.register(r"", ResidencyViewSet, basename="residency")
urlpatterns: List[URLPattern] = [
    path("", include(router.urls)),
]

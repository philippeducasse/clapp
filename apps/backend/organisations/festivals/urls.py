from typing import List

from django.urls import URLPattern, include, path
from rest_framework.routers import DefaultRouter

from organisations.festivals.views import FestivalViewSet

router: DefaultRouter = DefaultRouter()
router.register(r"", FestivalViewSet, basename="festival")
urlpatterns: List[URLPattern] = [
    path("", include(router.urls)),
]

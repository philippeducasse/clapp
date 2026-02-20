from django.urls import path, include, URLPattern
from rest_framework.routers import DefaultRouter
from organisations.festivals.views import FestivalViewSet
from typing import List

router: DefaultRouter = DefaultRouter(trailing_slash=False)
router.register(r"", FestivalViewSet, basename="festival")
urlpatterns: List[URLPattern] = [
    path("", include(router.urls)),
]

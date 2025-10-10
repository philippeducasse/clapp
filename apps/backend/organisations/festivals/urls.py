from django.urls import path, include, URLPattern
from rest_framework.routers import DefaultRouter
from festivals.views import FestivalViewSet
from typing import List

router: DefaultRouter = DefaultRouter()
router.register(r"", FestivalViewSet, basename="festival")
urlpatterns: List[URLPattern] = [
    path("", include(router.urls)),
]

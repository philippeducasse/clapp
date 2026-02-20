from typing import List

from django.urls import URLPattern, include, path
from rest_framework.routers import DefaultRouter

from applications.views import ApplicationViewSet

router: DefaultRouter = DefaultRouter()
router.register(r"", ApplicationViewSet, basename="application")
urlpatterns: List[URLPattern] = [
    path("", include(router.urls)),
]

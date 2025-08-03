from django.urls import path, include, URLPattern
from rest_framework.routers import DefaultRouter
from applications.views import ApplicationViewSet
from typing import List

router: DefaultRouter = DefaultRouter()
router.register(r"", ApplicationViewSet, basename="application")
urlpatterns: List[URLPattern] = [
    path("", include(router.urls)),
]
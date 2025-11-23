from django.urls import path, include, URLPattern
from rest_framework.routers import DefaultRouter
from performances.views import PerformanceViewSet, get_user_performances
from typing import List

router: DefaultRouter = DefaultRouter()
router.register(r"", PerformanceViewSet, basename="performance")
urlpatterns: List[URLPattern] = [
    path("", include(router.urls)),
    path("<int:user_id>/", get_user_performances),
]

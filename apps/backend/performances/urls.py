from typing import List

from django.urls import URLPattern, include, path
from rest_framework.routers import DefaultRouter

from performances.views import PerformanceViewSet, get_user_performances

router: DefaultRouter = DefaultRouter(trailing_slash=False)
router.register(r"", PerformanceViewSet, basename="performance")
urlpatterns: List[URLPattern] = [
    path("", include(router.urls)),
    path("<int:user_id>", get_user_performances),
]

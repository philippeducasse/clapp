from django.urls import path, include
from rest_framework.routers import DefaultRouter
from festivals.views import FestivalViewSet

router = DefaultRouter()
router.register(r'festivals', FestivalViewSet)
urlpatterns = [
    path("", include(router.urls)),
]
from typing import List

from django.urls import URLPattern, include, path
from rest_framework.routers import DefaultRouter

from applications.views import ApplicationViewSet, InboundEmailViewSet

router: DefaultRouter = DefaultRouter()
router.register(r"", ApplicationViewSet, basename="application")
urlpatterns: List[URLPattern] = [
    path("", include(router.urls)),
]

inbound_router: DefaultRouter = DefaultRouter()
inbound_router.register(r"", InboundEmailViewSet, basename="inbound-email")
inbound_email_urlpatterns: List[URLPattern] = [
    path("", include(inbound_router.urls)),
]

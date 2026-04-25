from typing import List

from django.contrib import admin
from django.http import JsonResponse
from django.urls import URLPattern, include, path

urlpatterns: List[URLPattern] = [
    path("admin/", admin.site.urls),
    path("health/", lambda request: JsonResponse({"status": "ok"})),
    path("sentry-debug/", lambda request: 1 / 0),
    path(
        "api/",
        include(
            [
                path("organisations/", include("organisations.urls")),
                path("festivals/", include("organisations.festivals.urls")),
                path("applications/", include("applications.urls")),
                path("performances/", include("performances.urls")),
                path("residencies/", include("organisations.residencies.urls")),
                path("venues/", include("organisations.venues.urls")),
                path("profiles/", include("profiles.urls")),
                path("support/", include("support.urls")),
            ]
        ),
    ),
]

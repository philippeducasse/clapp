from django.contrib import admin
from django.urls import path, include, URLPattern
from typing import List

urlpatterns: List[URLPattern] = [
    path("admin/", admin.site.urls),
    path(
        "api/",
        include(
            [
                path("festivals/", include("festivals.urls")),
                path("applications/", include("applications.urls")),
                path("performances/", include("performances.urls")),
                path("residencies/", include("residencies.urls")),
                path("venues/", include("venues.urls")),
                path("profiles/", include("profiles.urls")),
            ]
        ),
    ),
]

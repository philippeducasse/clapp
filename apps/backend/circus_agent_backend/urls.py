from django.contrib import admin
from django.urls import path, include, URLPattern
from typing import List

urlpatterns: List[URLPattern] = [
    path("admin/", admin.site.urls),
    path("api/", include([
        path('festivals/', include('festivals.urls')),
        path('applications/', include('applications.urls')),
    ])),
]

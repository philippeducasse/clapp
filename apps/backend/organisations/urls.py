from typing import List

from django.urls import URLPattern, path

from .views import search

urlpatterns: List[URLPattern] = [
    path("search/", search, name="organisations-search"),
]

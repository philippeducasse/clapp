from django.urls import path, URLPattern
from .views import search
from typing import List

urlpatterns: List[URLPattern] = [
    path("search/", search, name="organisations-search"),
]

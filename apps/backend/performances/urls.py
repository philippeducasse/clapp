from django.urls import path, URLPattern
from performances.views import get_user_performances
from typing import List

urlpatterns: List[URLPattern] = [
    path("<int:user_id>/", get_user_performances),
]

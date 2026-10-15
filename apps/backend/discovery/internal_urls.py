"""/internal/discovery/ — used by the discovery service only (service token)."""

from django.urls import path

from discovery import views

urlpatterns = [
    path("runs/<int:pk>/", views.update_run, name="discovery-internal-run"),
    path(
        "runs/<int:pk>/candidates/",
        views.create_candidates,
        name="discovery-internal-candidates",
    ),
    path("known-index/", views.get_known_index, name="discovery-internal-known-index"),
    path("sources/", views.upsert_sources, name="discovery-internal-sources"),
]

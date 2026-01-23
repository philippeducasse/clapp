from django.urls import path
from .views import SubmitBugReportView

urlpatterns = [
    path("bugs/", SubmitBugReportView.as_view(), name="submit-bug"),
]

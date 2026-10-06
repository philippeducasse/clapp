from rest_framework import status
from rest_framework.response import Response

from .models import APPLICATION_STATUS, Application


def set_application_status(application: Application, new_status: str, note=None):
    current_status = application.status
    if new_status not in {value for value, _ in APPLICATION_STATUS}:
        return Response(
            {"error": "Invalid application status"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    if current_status != new_status:
        application.status = new_status
        application.comments = note
        application.save()

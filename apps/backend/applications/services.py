from typing import Optional

from rest_framework.exceptions import ValidationError

from .models import APPLICATION_STATUS, Application


def set_application_status(
    application: Application, new_status: str, note: Optional[str] = None
) -> Application:
    """Set a new status. An optional note is added to the application's comments."""
    if new_status not in dict(APPLICATION_STATUS):
        raise ValidationError({"error": f"Invalid application status: {new_status}"})

    application.status = new_status
    if note and note not in (application.comments or ""):
        application.comments = f"{application.comments}\n{note}".strip()
    application.save()
    return application

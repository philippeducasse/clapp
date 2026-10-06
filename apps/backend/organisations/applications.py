from typing import Any, List

from django.utils import timezone

from applications.models import Application
from organisations.models import Organisation
from performances.models import Performance
from profiles.models import Profile


def create_form_application(
    organisation: Organisation,
    performances: List[Performance],
    default_profile: Profile,
    comments: str,
) -> Application:
    application = Application.objects.create(
        application_method="FORM",
        organisation=organisation,
        profile=default_profile,
        comments=comments,
        status="APPLIED",
        application_date=timezone.now().date(),
    )

    if performances:
        application.performances.set(performances)
        application.save()

    return application



def parse_performance_ids(performance_ids: Any) -> List[Performance]:
    """
    Parse performance IDs from various input formats and return Performance objects.

    Args:
        performance_ids: Can be a comma-separated string, list of IDs, or single ID

    Returns:
        List of Performance objects
    """
    if not performance_ids:
        return []

    if isinstance(performance_ids, str):
        ids = [int(id.strip()) for id in performance_ids.split(",") if id.strip()]
    elif isinstance(performance_ids, list):
        ids = [int(id) for id in performance_ids]
    else:
        ids = [int(performance_ids)]

    return list(Performance.objects.filter(id__in=ids))


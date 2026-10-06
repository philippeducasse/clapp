from celery import shared_task

from applications.inbox import check_inbox


@shared_task
def check_inbox_task() -> int:
    return check_inbox()

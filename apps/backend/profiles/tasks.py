import logging

from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail
from django.utils import timezone

from profiles.models import Reminder

logger = logging.getLogger(__name__)


@shared_task
def check_and_set_reminders() -> int:
    """
    Check for due reminders and send notifications.
    Runs every hour via Celery Beat.
    """

    now = timezone.now()

    due_reminders = Reminder.objects.filter(remind_at__lte=now, is_sent=False)

    sent_count = 0

    for reminder in due_reminders:
        try:
            send_reminder_notification(reminder)
            reminder.is_sent = True
            reminder.save()
            sent_count += 1

        except Exception as e:
            logger.error(f"Failed to send reminder {reminder.id}: {str(e)}")

    logger.info(f"Sent {sent_count} reminders")

    return sent_count


def send_reminder_notification(reminder: Reminder):
    subject = f"Reminder: {reminder.organisation.name}"
    message = f"""
Hello,

This is your reminder about {reminder.organisation.name}:

{reminder.message}

Organisation details:
- Name: {reminder.organisation.name}
- Website: {reminder.organisation.website_url or "N/A"}

Best regards,
Clapp Team
    """.strip()

    send_mail(
        subject=subject,
        message=message,
        from_email=settings.EMAIL_HOST_USER,
        recipient_list=[reminder.profile.email],
        fail_silently=False,
    )

import logging
import secrets

from celery import shared_task
from django.conf import settings
from django.core.mail import EmailMultiAlternatives, send_mail
from django.template.loader import render_to_string
from django.utils import timezone

from profiles.models import Profile, Reminder

logger = logging.getLogger(__name__)


@shared_task
def send_registration_confirmation_email(new_user_email: str):
    try:
        user = Profile.objects.get(email=new_user_email)
    except Profile.DoesNotExist:
        logger.error(f"User with email {new_user_email} not found for confirmation email task")
        return

    token = secrets.token_urlsafe(32)
    user.confirmation_token = token
    user.save()
    confirmation_url = f"{settings.APP_URL}/api/profiles/confirm-email?token={token}"

    logger.info(f"Created confirmation token for {user.email} : {token}")
    logger.info(f"Sending confirmation email from {settings.EMAIL_HOST_USER} to {user.email}")

    logger.info(
        f"DEBUG: USER: {settings.EMAIL_HOST_USER} \n PW: {settings.EMAIL_HOST_PASSWORD} \n PORT:{settings.EMAIL_PORT} \nEMAIL_USE_TLS: {settings.EMAIL_USE_TLS} HOST:\n{settings.EMAIL_HOST}"
    )

    context = {
        "email": user.email,
        "confirmation_url": confirmation_url,
    }

    text_content = f"""Welcome to Clapp!

        Hello {user.email or "there"},

        We're thrilled to have you join our performance arts community! Whether you're a juggler, singer-songwriter, or visual artist, Clapp will help you manage your freelance artist application process.

        Confirm Your Email: {confirmation_url}

        Let the show begin!
        The Clapp Team
            """.strip()

    html_content = render_to_string("profiles/emails/confirmation_email.html", context)

    email_message = EmailMultiAlternatives(
        subject="Welcome to Clapp! Please confirm your email",
        body=text_content,
        from_email=settings.EMAIL_HOST_USER,
        to=[user.email],
    )
    email_message.attach_alternative(html_content, "text/html")
    email_message.send(fail_silently=False)


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

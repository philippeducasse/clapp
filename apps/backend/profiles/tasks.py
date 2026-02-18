import logging
import secrets

from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail
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
    confirmation_url = f"{settings.APP_URL}/api/profiles/confirm-email?token={token}/"

    email_body = f"""
    <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <h2 style="color: #8B4789;">Welcome to Clapp! 🎪</h2>
                
                <p>Hello {user.email or "there"},</p>
                
                <p>We're thrilled to have you join our performance arts community! Whether you're a juggler, singer-songwriter, or visual artist, Clapp will help you manage your freelance artist application process.</p>
                
                <p style="margin: 30px 0; text-align: center;">
                    <a href="{confirmation_url}" style="background-color: #8B4789; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; display: inline-block;">
                        Confirm Your Email
                    </a>
                </p>
                
                <p style="margin-top: 40px; border-top: 1px solid #ddd; padding-top: 20px; font-size: 12px; color: #666;">
                    Let the show begin! 🎭<br>
                    The Clapp Team
                </p>
            </div>
        </body>
    </html>
    """

    logger.info(f"Created confirmation token for {user.email} : {token}")

    logger.info(f"Sending confirmation email from {settings.APP_EMAIL} to {user.email}")

    send_mail(
        "Welcome to Clapp! Please confirm your email",
        email_body,
        settings.APP_EMAIL,
        [user.email],
        fail_silently=False,
    )


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

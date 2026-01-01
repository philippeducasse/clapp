import logging

from django.core.mail import send_mail
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Profile

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Profile, dispatch_uid="send_confirmation_email")
def send_confirmation_email(sender, instance, created, **kwargs):
    logger.info(f"Sending confirmation email to {instance.email}")

    if created:
        send_mail(
            "Welcome! Please confirm your email",
            "CONFIRMATION URL GOES HERE",
            "info@philippeducasse.com",
            [instance.email],
            fail_silently=False,
        )

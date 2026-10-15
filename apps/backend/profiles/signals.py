import logging

from django.conf import settings
from django.db import transaction
from django.db.models.signals import post_save
from django.dispatch import receiver

from organisations.seeding import clone_all_seeds_for_profile

from .models import Profile
from .tasks import send_registration_confirmation_email

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Profile, dispatch_uid="send_confirmation_email")
def send_confirmation_email(sender, instance, created, raw, **kwargs):
    if raw:
        return

    if settings.ENVIRONMENT != "prod":
        logger.info(f"Skipping confirmation email for {instance.email}")
        return

    if created:
        logger.info(
            f"Initiating celery send_confirmaton_email task for user email: {instance.email}"
        )
        # Waits for database transaction to be complete before running this function
        transaction.on_commit(lambda: send_registration_confirmation_email.delay(instance.email))


@receiver(post_save, sender=Profile, dispatch_uid="seed_user_organisations")
def seed_user_organisations(sender, instance, created, raw, **kwargs):
    """When a new user registers, give them their own copy of every seed organisation.

    Seed organisations (user=NULL) are shared templates; see `organisations.seeding`.
    """
    if not created or raw:
        return

    logger.info(f"Seeding organisations for new user {instance.email} (id={instance.id})")
    clone_all_seeds_for_profile(instance)
    logger.info(f"Finished seeding organisations for user {instance.id}")

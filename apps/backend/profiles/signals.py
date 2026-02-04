import logging

from django.conf import settings
from django.db import connection
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Profile
from .tasks import send_registration_confirmation_email

logger = logging.getLogger(__name__)


class SchemaCreationError(Exception):
    """Raised when schema creation fails"""

    pass


@receiver(post_save, sender=Profile, dispatch_uid="send_confirmation_email")
def send_confirmation_email(sender, instance, created, raw, **kwargs):
    if raw:
        return  # Skip during fixture loading (loaddata)

    if created:
        send_registration_confirmation_email.delay(instance.email)


@receiver(post_save, sender=Profile, dispatch_uid="create_database_schema")
def create_database_schema(sender, instance, created, **kwargs):
    """
    - sender - The model class that sent the signal (Profile)
    - instance - The actual Profile object that was saved
    - created - Boolean: True if a new object was created, False if an existing one was updated
    - raw - Boolean: True if data is being loaded via fixtures/loaddata (we skip in that case)
    - **kwargs - Other optional keyword arguments
    """
    if not created:
        return

    if settings.ENVIRONMENT != "prod":
        return

    logger.info(f"Creating database schema for user {instance.email}")

    schema_name = f"user_{instance.id}"
    quoted_schema = connection.ops.quote_name(schema_name)

    tables = [
        "venues_venue",
        "venues_venuecontact",
        "festivals_festival",
        "festivals_festivalcontact",
        "residencies_residency",
        "residencies_residencycontact",
    ]

    try:
        with connection.cursor() as cursor:
            cursor.execute(f"CREATE SCHEMA IF NOT EXISTS {quoted_schema}")

            for table in tables:
                quoted_table = connection.ops.quote_name(table)
                cursor.execute(f"""
                    CREATE TABLE IF NOT EXISTS {quoted_schema}.{quoted_table}
                    (LIKE template.{quoted_table} INCLUDING ALL)
                """)

                cursor.execute(f"""
                    INSERT INTO {quoted_schema}.{quoted_table}
                    SELECT * FROM template.{quoted_table}
                """)

            logger.info(f"Schema {schema_name} created successfully for user {instance.email}")
    except Exception as e:
        logger.error(f"Failed to create schema {schema_name} for user {instance.email}: {e}")
        raise SchemaCreationError(f"Could not create schema for user {instance.id}") from e

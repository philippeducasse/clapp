import logging

from django.core.mail import send_mail
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Profile

logger = logging.getLogger(__name__)


class SchemaCreationError(Exception):
    """Raised when schema creation fails"""

    pass


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


# @receiver(post_save, sender=Profile, dispatch_uid="create_database_schema")
# def create_database_schema(sender, instance, created, **kwargs):
#     if not created:
#         return

#     logger.info(f"Creating database schema for user {instance.email}")

#     schema_name = f"user_{instance.id}"
#     quoted_schema = connection.ops.quote_name(schema_name)

#     tables = ["festivals", "venues", "residencies"]

#     try:
#         with connection.cursor() as cursor:
#             cursor.execute(f"CREATE SCHEMA IF NOT EXISTS {quoted_schema}")

#             for table in tables:
#                 quoted_table = connection.ops.quote_name(table)
#                 cursor.execute(f"""
#                     CREATE TABLE IF NOT EXISTS {quoted_schema}.{quoted_table}
#                     (LIKE template.{quoted_table} INCLUDING ALL)
#                 """)

#                 cursor.execute(f"""
#                     INSERT INTO {quoted_schema}.{quoted_table}
#                     SELECT * FROM template.{quoted_table}
#                 """)

#             logger.info(f"Schema {schema_name} created successfully for user {instance.email}")
#     except Exception as e:
#         logger.error(f"Failed to create schema {schema_name} for user {instance.email}: {e}")
#         raise SchemaCreationError(f"Could not create schema for user {instance.id}") from e

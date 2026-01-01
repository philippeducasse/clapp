import logging
import os

from django.db.models.signals import post_delete
from django.dispatch import receiver

from .models import Performance

logger = logging.getLogger(__name__)


@receiver(post_delete, sender=Performance)
def delete_profile_dossier(sender, instance, **kwargs):
    logger.info(f"Deleting dossiers for performance {instance.performance_title}")
    if instance.dossiers:
        for dossier in instance.dossiers.all():
            if os.path.isfile(dossier.file.path):
                os.remove(dossier.file.path)
                logger.info(f"Deleting dossier {dossier.file.path}")

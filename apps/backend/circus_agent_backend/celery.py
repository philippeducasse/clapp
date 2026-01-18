import os

from celery import Celery
from celery.schedules import crontab

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "conf.settings.local")

app = Celery("cab")

app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()

EVERY_HOUR = 0

app.conf.beat_schedule = {
    "check-reminders-every-hour": {
        "task": "profiles.tasks.check_and_set_reminders",
        "schedule": crontab(minute=EVERY_HOUR),
    }
}

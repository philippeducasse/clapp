from django.db import migrations
from django.db.models.functions import TruncDate


def backfill_application_date(apps, schema_editor):
    """Non-draft applications created manually were saved without a date; use their creation date."""
    Application = apps.get_model("applications", "Application")
    Application.objects.filter(application_date__isnull=True).exclude(status="DRAFT").update(
        application_date=TruncDate("created_at")
    )


class Migration(migrations.Migration):
    dependencies = [
        ("applications", "0018_applicationseason_is_default"),
    ]

    operations = [
        migrations.RunPython(backfill_application_date, migrations.RunPython.noop),
    ]

from django.db import migrations, models


def populate_name_from_year(apps, schema_editor):
    ApplicationSeason = apps.get_model("applications", "ApplicationSeason")
    for season in ApplicationSeason.objects.all():
        season.name = str(season.year)
        season.save(update_fields=["name"])


def populate_year_from_name(apps, schema_editor):
    ApplicationSeason = apps.get_model("applications", "ApplicationSeason")
    for season in ApplicationSeason.objects.all():
        try:
            season.year = int(season.name)
        except ValueError:
            season.year = None
        season.save(update_fields=["year"])


class Migration(migrations.Migration):
    dependencies = [
        ("applications", "0013_applicationseason_application_season"),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name="applicationseason",
            unique_together=set(),
        ),
        migrations.AlterField(
            model_name="applicationseason",
            name="name",
            field=models.CharField(max_length=100, blank=True, default=""),
        ),
        migrations.RunPython(populate_name_from_year, populate_year_from_name),
        migrations.RemoveField(
            model_name="applicationseason",
            name="year",
        ),
        migrations.AlterField(
            model_name="applicationseason",
            name="name",
            field=models.CharField(max_length=100),
        ),
        migrations.AlterModelOptions(
            name="applicationseason",
            options={"ordering": ["-created_at"]},
        ),
        migrations.AlterUniqueTogether(
            name="applicationseason",
            unique_together={("name", "profile")},
        ),
    ]
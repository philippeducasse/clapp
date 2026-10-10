from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("applications", "0017_inbound_email_form_match"),
    ]

    operations = [
        migrations.AddField(
            model_name="applicationseason",
            name="is_default",
            field=models.BooleanField(
                default=False,
                help_text="Default season preselected on new applications. At most one per profile.",
            ),
        ),
        migrations.AddConstraint(
            model_name="applicationseason",
            constraint=models.UniqueConstraint(
                condition=models.Q(("is_default", True)),
                fields=("profile",),
                name="unique_default_season_per_profile",
            ),
        ),
    ]

import csv
from organisations.festivals.models import Festival
import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "conf.settings.local")
django.setup()

with open("../festivals_data.csv", "r") as file:
    reader = csv.DictReader(file)
    for row in reader:
        Festival.objects.create(
            festival_name=row["festival_name"],
            description=row.get("description", ""),
            country=row.get("country", ""),
            town=row.get("town", ""),
            festival_type=row.get("festival_type", "STREET"),
            website_url=row.get("website_url", ""),
            contact_email=row.get("contact_email", ""),
            contact_person=row.get("contact_person", ""),
            start_date=row.get("start_date", None),
            end_date=row.get("end_date", None),
            approximate_date=row.get("approximate_date", ""),
            application_date_start=row.get("application_date_start", ""),
            application_date_end=row.get("application_date_end", ""),
            application_type=row.get("application_type", "UNKNOWN"),
            applied=row.get("applied", False),
            comments=row.get("comments", ""),
        )

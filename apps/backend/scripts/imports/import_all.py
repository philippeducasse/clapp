import pandas as pd
from datetime import datetime, date
from organisations.residencies.models import Residency
from organisations.venues.models import Venue
from organisations.festivals.models import Festival
from typing import Optional, Any

import os
import sys
import django

# Add the project directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Set up Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "conf.settings.local")
django.setup()


def parse_date(val: Any) -> Optional[date]:
    if pd.isna(val):
        return None
    if isinstance(val, datetime):
        return val.date()
    try:
        return pd.to_datetime(val, errors="coerce").date()
    except Exception:
        return None


# Load the CSV with correct delimiter
df: pd.DataFrame = pd.read_csv("scripts/data/only_festivals.csv", delimiter=",", dtype=str)

# Normalize column names
df.columns = [col.strip().upper() for col in df.columns]

for index, row in df.iterrows():
    entry_type: str = str(row.get("EVENT_TYPE", "") or "").strip().lower()
    name: str = str(row.get("NAME", "") or "").strip().lower()

    if not name:
        continue

    if entry_type == "festival" or entry_type == "juggling convention":
        if Festival.objects.filter(festival_name__iexact=name).exists():
            print(f"Skipping row {index}: Festival '{name}' already exists in the database")
            continue

        festival: Festival = Festival(
            festival_name=name,
            country=str(row.get("COUNTRY", "") or "").strip(),
            festival_type="STREET",  # default
            website_url=str(row.get("WEBSITE", "") or "").strip(),
            contact_email=str(row.get("E-MAIL", "") or "").strip(),
            contact_person=str(row.get("CONTACT", "") or "").strip(),
            approximate_date=str(row.get("DATE", "") or "").strip(),
            applied=False,
            comments=str(row.get("COMMENTS", "") or "").strip(),
        )

        festival.save()
        print(f"Imported: {festival.festival_name}")

    elif "residenc" in name or "residenc" in entry_type:
        print("importing residency: ", name)

        if Residency.objects.filter(residency_name__iexact=name).exists():
            print(f"Skipping row {index}: Residency '{name}' already exists in the database")
            continue

        residency: Residency = Residency(
            residency_name=name,
            country=str(row.get("COUNTRY", "") or "").strip(),
            website_url=str(row.get("WEBSITE", "") or "").strip(),
            contact_email=str(row.get("E-MAIL", "") or "").strip(),
            contact_person=str(row.get("CONTACT", "") or "").strip(),
            approximate_date=str(row.get("DATE", "") or "").strip(),
            applied=False,
            comments=str(row.get("COMMENTS", "") or "").strip(),
        )

        residency.save()
        print(f"Imported: {residency.residency_name}")

    else:
        if Venue.objects.filter(venue_name__iexact=name).exists():
            print(f"Skipping row {index}: Residency '{name}' already exists in the database")
            continue

        venue: Venue = Venue(
            venue_name=name,
            country=str(row.get("COUNTRY", "") or "").strip(),
            website_url=str(row.get("WEBSITE", "") or "").strip(),
            contact_email=str(row.get("E-MAIL", "") or "").strip(),
            contact_person=str(row.get("CONTACT", "") or "").strip(),
            contacted=False,
            comments=str(row.get("COMMENTS", "") or "").strip(),
        )

        venue.save()
        print(f"Imported: {venue.venue_name}")

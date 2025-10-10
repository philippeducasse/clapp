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
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "circus_agent_backend.settings")
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
df: pd.DataFrame = pd.read_csv("scripts/data/all_events.csv", delimiter=",", dtype=str)

# Normalize column names
df.columns = [col.strip().upper() for col in df.columns]

for index, row in df.iterrows():
    entry_type: str = str(row.get("EVENT_TYPE", "") or "").strip().lower()
    name: str = str(row.get("NAME", "") or "").strip()

    if not name:
        continue

    email = str(row.get("E-MAIL", "") or "").strip()

    if entry_type == "festival" or entry_type == "juggling convention":
        try:
            festival = Festival.objects.get(festival_name__iexact=name)
            festival.contact_email = email
            festival.save()
            print(f"✓ Updated festival: {festival.festival_name}")
        except Festival.DoesNotExist:
            print(f"✗ Festival not found: {name}")
        except Festival.MultipleObjectsReturned:
            print(f"⚠ Multiple festivals found for: {name}")

    elif "residenc" in name.lower() or "residenc" in entry_type:
        try:
            residency = Residency.objects.get(residency_name__iexact=name)
            residency.contact_email = email
            residency.save()
            print(f"✓ Updated residency: {residency.residency_name}")
        except Residency.DoesNotExist:
            print(f"✗ Residency not found: {name}")
        except Residency.MultipleObjectsReturned:
            print(f"⚠ Multiple residencies found for: {name}")

    else:
        try:
            venue = Venue.objects.get(venue_name__iexact=name)
            venue.contact_email = email
            venue.save()
            print(f"✓ Updated venue: {venue.venue_name}")
        except Venue.DoesNotExist:
            print(f"✗ Venue not found: {name}")
        except Venue.MultipleObjectsReturned:
            print(f"⚠ Multiple venues found for: {name}")

print("\n✅ Import completed!")

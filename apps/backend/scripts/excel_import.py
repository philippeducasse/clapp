import pandas as pd
from datetime import datetime
from festivals.models import Festival


def parse_date(val):
    if pd.isna(val):
        return None
    if isinstance(val, datetime):
        return val.date()
    try:
        return pd.to_datetime(val, errors="coerce").date()
    except Exception:
        return None


# Load the CSV with correct delimiter
df = pd.read_csv("scripts/excel_import.csv", delimiter=";", dtype=str)

# Normalize column names
df.columns = [col.strip().upper() for col in df.columns]

for index, row in df.iterrows():
    name = str(row.get("NAME", "") or "").strip()

    if not name:
        print(f"Skipping row {index}: Missing festival name")
        continue

    festival = Festival(
        festival_name=name,
        country=str(row.get("COUNTRY", "") or "").strip(),
        town=str(row.get("TOWN", "") or "").strip(),
        festival_type="STREET",  # default
        website_url=str(row.get("WEBSITE", "") or "").strip(),
        contact_email=str(row.get("EMAIL", "") or "").strip(),
        contact_person=str(row.get("CONTACT PERSON", "") or "").strip(),
        start_date=parse_date(row.get("START DATE") if "START DATE" in row else None),
        end_date=parse_date(row.get("END DATE") if "END DATE" in row else None),
        date_text=str(row.get("EVENT DATE", "") or "").strip(),
        applied=bool(float(row.get("APPLIED 2023", "0") or 0))
        or bool(float(row.get("APPLIED 2025", "0") or 0)),
        comments=str(row.get("COMMENT", "") or "").strip(),
    )

    festival.save()
    print(f"Imported: {festival.festival_name}")

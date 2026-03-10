import io
import logging
from typing import Dict

from celery import shared_task
from django.contrib.auth import get_user_model
from organisations.festivals.models import Festival, FestivalContact
from organisations.residencies.models import Residency, ResidencyContact
from organisations.venues.models import Venue, VenueContact
import pandas as pd
from organisations.utils import normalize_domain

logger = logging.getLogger(__name__)


@shared_task
def upload_user_data(file_bytes: bytes, user_id: int):
    User = get_user_model()
    user = User.objects.get(pk=user_id)
    try:
        df: pd.DataFrame = pd.read_excel(io.BytesIO(file_bytes), dtype=str)
    except Exception as e:
        logger.error(f"Failed to read Excel file: {str(e)}")
        return {"error": f"Invalid Excel file: {str(e)}"}

    stats = {
        "festivals_imported": 0,
        "festivals_skipped": 0,
        "residencies_imported": 0,
        "residencies_skipped": 0,
        "venues_imported": 0,
        "venues_skipped": 0,
        "errors": [],
    }

    type_config = {
        "festival": {
            "model": Festival,
            "contact_model": FestivalContact,
            "contact_fk": "festival",
            "stats_key": "festivals",
        },
        "residency": {
            "model": Residency,
            "contact_model": ResidencyContact,
            "contact_fk": "residency",
            "stats_key": "residencies",
        },
        "venue": {
            "model": Venue,
            "contact_model": VenueContact,
            "contact_fk": "venue",
            "stats_key": "venues",
        },
    }

    def get_cell(row_dict: Dict[str, str], key: str, default: str = "") -> str:
        """Get value from row dict with case-insensitive key lookup."""
        key_lower = key.lower()
        for k, v in row_dict.items():
            if k.lower() == key_lower:
                return "" if pd.isna(v) else str(v).strip()
        return default

    def domain_exists(model_class, website: str, index: int) -> bool:
        if not website:
            return False
        normalized_domain = normalize_domain(website)
        if model_class.objects.filter(website_url__icontains=normalized_domain, user=user).exists():
            logger.info(
                f"Row {index}: {model_class._meta.object_name} with domain '{normalized_domain}' already exists"
            )
            return True
        return False

    def resolve_org_type(name: str, organisation_type: str) -> str | None:
        if "festival" in name or organisation_type == "festival":
            return "festival"
        if "residenc" in name or "residenc" in organisation_type:
            return "residency"
        if organisation_type == "venue":
            return "venue"
        return None

    try:
        for index, row in df.iterrows():
            try:
                row_dict = {k.lower(): v for k, v in row.to_dict().items()}

                name = get_cell(row_dict, "name").lower()
                organisation_type = get_cell(
                    row_dict, "type", get_cell(row_dict, "event_type")
                ).lower()

                if not name:
                    continue

                resolved_type = resolve_org_type(name, organisation_type)
                if not resolved_type:
                    error_msg = f"Row {index}: Invalid organisation type: {organisation_type}"
                    logger.error(error_msg)
                    stats["errors"].append(error_msg)
                    continue

                config = type_config[resolved_type]
                model_class = config["model"]
                stats_key = config["stats_key"]

                contact_email = get_cell(row_dict, "email")
                contact_person = get_cell(row_dict, "contact")
                country = get_cell(row_dict, "country")
                website = get_cell(row_dict, "website")
                date_str = get_cell(row_dict, "date")
                comments = get_cell(row_dict, "comments")

                if model_class.objects.filter(name__iexact=name, user=user).exists():
                    logger.info(f"Row {index}: {resolved_type} '{name}' already exists")
                    stats[f"{stats_key}_skipped"] += 1
                    continue

                if domain_exists(model_class, website, index):
                    stats[f"{stats_key}_skipped"] += 1
                    continue

                fields = {
                    "name": name,
                    "country": country,
                    "website_url": website,
                    "comments": comments,
                    "user": user,
                }
                if model_class != Venue:
                    fields["approximate_date"] = date_str

                org = model_class(**fields)
                org.save()

                if contact_email:
                    config["contact_model"].objects.create(
                        name=contact_person,
                        email=contact_email,
                        user=user,
                        **{config["contact_fk"]: org},
                    )

                logger.info(f"Imported {resolved_type}: {org.name}")
                stats[f"{stats_key}_imported"] += 1

            except Exception as e:
                error_msg = f"Row {index}: {str(e)}"
                logger.error(error_msg)
                stats["errors"].append(error_msg)

        logger.info(
            f"Upload completed: {stats['festivals_imported']} festivals, "
            f"{stats['residencies_imported']} residencies, {stats['venues_imported']} venues"
        )
        return stats

    except Exception as e:
        logger.error(f"Unexpected error during upload: {str(e)}", exc_info=True)
        return {"error": f"Upload failed: {str(e)}"}

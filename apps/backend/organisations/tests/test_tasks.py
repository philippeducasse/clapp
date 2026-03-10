import io

import pandas as pd
import pytest

from organisations.festivals.models import Festival, FestivalContact
from organisations.residencies.models import Residency
from organisations.tasks import upload_user_data
from organisations.venues.models import Venue
from profiles.models import Profile


def make_excel(rows: list[dict]) -> bytes:
    """Build an in-memory Excel file from a list of row dicts."""
    df = pd.DataFrame(rows)
    buf = io.BytesIO()
    df.to_excel(buf, index=False)
    return buf.getvalue()


@pytest.fixture
def user(db):
    return Profile.objects.create_user(email="uploader@example.com", password="pass")


@pytest.mark.django_db
class TestUploadUserData:
    # --- happy paths ---

    def test_import_festival(self, user):
        file_bytes = make_excel(
            [
                {
                    "name": "Summer Festival",
                    "type": "festival",
                    "country": "France",
                    "website": "https://summerfest.com",
                    "email": "",
                    "contact": "",
                    "date": "",
                    "comments": "",
                },
            ]
        )
        result = upload_user_data(file_bytes, user.id)

        assert result["festivals_imported"] == 1
        assert Festival.objects.filter(name="summer festival", user=user).exists()

    def test_import_residency(self, user):
        file_bytes = make_excel(
            [
                {
                    "name": "Art Residency Paris",
                    "type": "residency",
                    "country": "France",
                    "website": "",
                    "email": "",
                    "contact": "",
                    "date": "",
                    "comments": "",
                },
            ]
        )
        result = upload_user_data(file_bytes, user.id)

        assert result["residencies_imported"] == 1
        assert Residency.objects.filter(name="art residency paris", user=user).exists()

    def test_import_venue(self, user):
        file_bytes = make_excel(
            [
                {
                    "name": "The Grand Venue",
                    "type": "venue",
                    "country": "Belgium",
                    "website": "",
                    "email": "",
                    "contact": "",
                    "date": "",
                    "comments": "",
                },
            ]
        )
        result = upload_user_data(file_bytes, user.id)

        assert result["venues_imported"] == 1
        assert Venue.objects.filter(name="the grand venue", user=user).exists()

    def test_import_creates_contact(self, user):
        file_bytes = make_excel(
            [
                {
                    "name": "Contact Festival",
                    "type": "festival",
                    "country": "Germany",
                    "website": "",
                    "email": "info@fest.com",
                    "contact": "Jane Doe",
                    "date": "",
                    "comments": "",
                },
            ]
        )
        upload_user_data(file_bytes, user.id)

        festival = Festival.objects.get(name="contact festival", user=user)
        contact = FestivalContact.objects.get(festival=festival)
        assert contact.email == "info@fest.com"
        assert contact.name == "Jane Doe"

    def test_no_contact_created_when_email_missing(self, user):
        file_bytes = make_excel(
            [
                {
                    "name": "No Contact Festival",
                    "type": "festival",
                    "country": "France",
                    "website": "",
                    "email": "",
                    "contact": "",
                    "date": "",
                    "comments": "",
                },
            ]
        )
        upload_user_data(file_bytes, user.id)

        festival = Festival.objects.get(name="no contact festival", user=user)
        assert FestivalContact.objects.filter(festival=festival).count() == 0

    def test_type_inferred_from_name(self, user):
        """Org type should be resolved from the name when the type column is ambiguous."""
        file_bytes = make_excel(
            [
                {
                    "name": "Berlin Festival",
                    "type": "",
                    "country": "Germany",
                    "website": "",
                    "email": "",
                    "contact": "",
                    "date": "",
                    "comments": "",
                },
            ]
        )
        result = upload_user_data(file_bytes, user.id)

        assert result["festivals_imported"] == 1

    def test_multiple_orgs_imported(self, user):
        file_bytes = make_excel(
            [
                {
                    "name": "Fest One",
                    "type": "festival",
                    "country": "France",
                    "website": "",
                    "email": "",
                    "contact": "",
                    "date": "",
                    "comments": "",
                },
                {
                    "name": "Venue One",
                    "type": "venue",
                    "country": "Belgium",
                    "website": "",
                    "email": "",
                    "contact": "",
                    "date": "",
                    "comments": "",
                },
                {
                    "name": "Art Residency",
                    "type": "residency",
                    "country": "Italy",
                    "website": "",
                    "email": "",
                    "contact": "",
                    "date": "",
                    "comments": "",
                },
            ]
        )
        result = upload_user_data(file_bytes, user.id)

        assert result["festivals_imported"] == 1
        assert result["venues_imported"] == 1
        assert result["residencies_imported"] == 1

    # --- duplicate skipping ---

    def test_skip_duplicate_name(self, user):
        Festival.objects.create(name="existing festival", user=user, country="France")

        file_bytes = make_excel(
            [
                {
                    "name": "Existing Festival",
                    "type": "festival",
                    "country": "France",
                    "website": "",
                    "email": "",
                    "contact": "",
                    "date": "",
                    "comments": "",
                },
            ]
        )
        result = upload_user_data(file_bytes, user.id)

        assert result["festivals_skipped"] == 1
        assert result["festivals_imported"] == 0

    def test_skip_duplicate_domain(self, user):
        Festival.objects.create(
            name="Some Other Name",
            user=user,
            country="France",
            website_url="https://www.myfest.com",
        )

        file_bytes = make_excel(
            [
                {
                    "name": "My Festival",
                    "type": "festival",
                    "country": "France",
                    "website": "https://myfest.com",
                    "email": "",
                    "contact": "",
                    "date": "",
                    "comments": "",
                },
            ]
        )
        result = upload_user_data(file_bytes, user.id)

        assert result["festivals_skipped"] == 1
        assert result["festivals_imported"] == 0

    def test_duplicate_check_is_per_user(self, user):
        """A name that exists for another user should still be imported."""
        other_user = Profile.objects.create_user(email="other@example.com", password="pass")
        Festival.objects.create(name="shared festival", user=other_user, country="France")

        file_bytes = make_excel(
            [
                {
                    "name": "Shared Festival",
                    "type": "festival",
                    "country": "France",
                    "website": "",
                    "email": "",
                    "contact": "",
                    "date": "",
                    "comments": "",
                },
            ]
        )
        result = upload_user_data(file_bytes, user.id)

        assert result["festivals_imported"] == 1

    # --- malformed / bad data ---

    def test_invalid_excel_bytes_returns_error(self, user):
        result = upload_user_data(b"this is not an excel file", user.id)

        assert "error" in result

    def test_row_with_no_name_is_skipped(self, user):
        file_bytes = make_excel(
            [
                {
                    "name": "",
                    "type": "festival",
                    "country": "France",
                    "website": "",
                    "email": "",
                    "contact": "",
                    "date": "",
                    "comments": "",
                },
            ]
        )
        result = upload_user_data(file_bytes, user.id)

        assert result["festivals_imported"] == 0
        assert result["errors"] == []

    def test_unresolvable_org_type_adds_error(self, user):
        file_bytes = make_excel(
            [
                {
                    "name": "Mystery Org",
                    "type": "unknowntype",
                    "country": "France",
                    "website": "",
                    "email": "",
                    "contact": "",
                    "date": "",
                    "comments": "",
                },
            ]
        )
        result = upload_user_data(file_bytes, user.id)

        assert len(result["errors"]) == 1
        assert "Invalid organisation type" in result["errors"][0]

    def test_missing_type_column_uses_name_inference(self, user):
        """Rows without a type column at all should fall back to name-based inference."""
        file_bytes = make_excel(
            [
                {
                    "name": "Jazz Residency Club",
                    "country": "Spain",
                    "website": "",
                    "email": "",
                    "contact": "",
                    "date": "",
                    "comments": "",
                },
            ]
        )
        result = upload_user_data(file_bytes, user.id)

        assert result["residencies_imported"] == 1

    def test_mixed_valid_and_invalid_rows(self, user):
        file_bytes = make_excel(
            [
                {
                    "name": "Good Festival",
                    "type": "festival",
                    "country": "France",
                    "website": "",
                    "email": "",
                    "contact": "",
                    "date": "",
                    "comments": "",
                },
                {
                    "name": "Bad Org",
                    "type": "unknowntype",
                    "country": "France",
                    "website": "",
                    "email": "",
                    "contact": "",
                    "date": "",
                    "comments": "",
                },
                {
                    "name": "",
                    "type": "venue",
                    "country": "Belgium",
                    "website": "",
                    "email": "",
                    "contact": "",
                    "date": "",
                    "comments": "",
                },
            ]
        )
        result = upload_user_data(file_bytes, user.id)

        assert result["festivals_imported"] == 1
        assert len(result["errors"]) == 1  # only the unknown type row

    def test_empty_spreadsheet_returns_zero_counts(self, user):
        file_bytes = make_excel([])
        result = upload_user_data(file_bytes, user.id)

        assert result["festivals_imported"] == 0
        assert result["residencies_imported"] == 0
        assert result["venues_imported"] == 0
        assert result["errors"] == []

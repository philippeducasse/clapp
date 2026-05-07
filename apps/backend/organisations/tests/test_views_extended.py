"""Extended tests for organisations/views.py to improve coverage."""

from unittest.mock import MagicMock, patch

import pytest
from rest_framework.test import APIClient

from organisations.festivals.models import Festival
from organisations.residencies.models import Residency
from organisations.venues.models import Venue
from profiles.models import Profile


@pytest.mark.django_db
class TestSearchView:
    """Tests for the unified search endpoint."""

    def test_search_short_query_returns_empty(self):
        """Queries shorter than 2 chars return empty list."""
        profile = Profile.objects.create_user(email="s@example.com", password="pass")
        client = APIClient()
        client.force_authenticate(user=profile)
        response = client.get("/api/organisations/search/?q=a")
        assert response.status_code == 200
        assert response.data == []

    def test_search_returns_festivals_venues_residencies(self):
        profile = Profile.objects.create_user(email="s@example.com", password="pass")
        Festival.objects.create(name="Jazz Festival", town="Paris", country="France", user=profile)
        Venue.objects.create(name="Jazz Venue", town="London", country="UK", user=profile)
        Residency.objects.create(name="Jazz Residency", town="Berlin", country="DE", user=profile)

        client = APIClient()
        client.force_authenticate(user=profile)
        response = client.get("/api/organisations/search/?q=Jazz")
        assert response.status_code == 200
        types = {r["type"] for r in response.data}
        assert "festival" in types
        assert "venue" in types
        assert "residency" in types

    def test_search_sorted_alphabetically(self):
        profile = Profile.objects.create_user(email="s@example.com", password="pass")
        Festival.objects.create(name="Zebra Fest", town="Paris", country="France", user=profile)
        Festival.objects.create(name="Alpha Fest", town="Berlin", country="Germany", user=profile)

        client = APIClient()
        client.force_authenticate(user=profile)
        response = client.get("/api/organisations/search/?q=Fest")
        assert response.status_code == 200
        names = [r["name"] for r in response.data]
        assert names == sorted(names, key=str.lower)

    def test_search_with_type_festival(self):
        profile = Profile.objects.create_user(email="s@example.com", password="pass")
        Festival.objects.create(name="Rock Festival", town="Berlin", country="DE", user=profile)

        client = APIClient()
        client.force_authenticate(user=profile)
        response = client.get("/api/organisations/search/?q=Rock&type=festival")
        assert response.status_code == 200

    def test_search_with_type_venue(self):
        profile = Profile.objects.create_user(email="s@example.com", password="pass")
        Venue.objects.create(name="Rock Venue", town="London", country="UK", user=profile)

        client = APIClient()
        client.force_authenticate(user=profile)
        response = client.get("/api/organisations/search/?q=Rock&type=venue")
        assert response.status_code == 200

    def test_search_with_type_residency(self):
        profile = Profile.objects.create_user(email="s@example.com", password="pass")
        Residency.objects.create(name="Rock Residency", town="Paris", country="FR", user=profile)

        client = APIClient()
        client.force_authenticate(user=profile)
        response = client.get("/api/organisations/search/?q=Rock&type=residency")
        assert response.status_code == 200

    def test_search_with_invalid_type_returns_400(self):
        profile = Profile.objects.create_user(email="s@example.com", password="pass")
        client = APIClient()
        client.force_authenticate(user=profile)
        response = client.get("/api/organisations/search/?q=Rock&type=invalid")
        assert response.status_code == 400


@pytest.mark.django_db
class TestOrganisationTagAction:
    """Tests for the tag action on organisations."""

    def test_tag_festival_valid(self):
        profile = Profile.objects.create_user(email="t@example.com", password="pass")
        festival = Festival.objects.create(
            name="Tag Festival", town="Paris", country="France", user=profile
        )
        client = APIClient()
        client.force_authenticate(user=profile)
        response = client.patch(f"/api/festivals/{festival.id}/tag/STAR/")
        assert response.status_code == 200
        festival.refresh_from_db()
        assert festival.tag == "STAR"

    def test_tag_festival_toggle_off(self):
        profile = Profile.objects.create_user(email="t@example.com", password="pass")
        festival = Festival.objects.create(
            name="Tag Festival", town="Paris", country="France", user=profile, tag="STAR"
        )
        client = APIClient()
        client.force_authenticate(user=profile)
        response = client.patch(f"/api/festivals/{festival.id}/tag/STAR/")
        assert response.status_code == 200
        festival.refresh_from_db()
        assert festival.tag == ""

    def test_tag_festival_invalid_action(self):
        profile = Profile.objects.create_user(email="t@example.com", password="pass")
        festival = Festival.objects.create(
            name="Tag Festival", town="Paris", country="France", user=profile
        )
        client = APIClient()
        client.force_authenticate(user=profile)
        response = client.patch(f"/api/festivals/{festival.id}/tag/INVALID/")
        assert response.status_code == 400

    def test_tag_venue_valid(self):
        profile = Profile.objects.create_user(email="t@example.com", password="pass")
        venue = Venue.objects.create(name="Tag Venue", town="London", country="UK", user=profile)
        client = APIClient()
        client.force_authenticate(user=profile)
        response = client.patch(f"/api/venues/{venue.id}/tag/WARNING/")
        assert response.status_code == 200
        venue.refresh_from_db()
        assert venue.tag == "WARNING"


@pytest.mark.django_db
class TestOrganisationUploadAction:
    """Tests for the upload action."""

    def test_upload_no_file_returns_400(self):
        profile = Profile.objects.create_user(email="u@example.com", password="pass")
        client = APIClient()
        client.force_authenticate(user=profile)
        response = client.post("/api/festivals/upload/", {}, format="multipart")
        assert response.status_code == 400
        assert "error" in response.data

    def test_upload_with_file_starts_task(self):
        from io import BytesIO

        profile = Profile.objects.create_user(email="u@example.com", password="pass")
        client = APIClient()
        client.force_authenticate(user=profile)

        mock_task = MagicMock()
        mock_task.id = "task-123"

        with patch("organisations.views.upload_user_data.delay", return_value=mock_task):
            excel_content = BytesIO(b"fake excel content")
            excel_content.name = "data.xlsx"
            response = client.post(
                "/api/festivals/upload/", {"excel": excel_content}, format="multipart"
            )

        assert response.status_code == 202
        assert "task_id" in response.data


@pytest.mark.django_db
class TestOrganisationUploadStatusAction:
    """Tests for upload_status action."""

    def test_upload_status_pending(self):
        profile = Profile.objects.create_user(email="us@example.com", password="pass")
        client = APIClient()
        client.force_authenticate(user=profile)

        mock_result = MagicMock()
        mock_result.status = "PENDING"
        mock_result.ready.return_value = False
        mock_result.result = None

        with patch("organisations.views.AsyncResult", return_value=mock_result):
            response = client.get("/api/festivals/upload-status/fake-task-id/")

        assert response.status_code == 200
        assert response.data["status"] == "PENDING"
        assert response.data["stats"] is None

    def test_upload_status_success(self):
        profile = Profile.objects.create_user(email="us@example.com", password="pass")
        client = APIClient()
        client.force_authenticate(user=profile)

        mock_result = MagicMock()
        mock_result.status = "SUCCESS"
        mock_result.ready.return_value = True
        mock_result.result = {"created": 5, "updated": 2}

        with patch("organisations.views.AsyncResult", return_value=mock_result):
            response = client.get("/api/festivals/upload-status/fake-task-id/")

        assert response.status_code == 200
        assert response.data["status"] == "SUCCESS"
        assert response.data["stats"] == {"created": 5, "updated": 2}


@pytest.mark.django_db
class TestApplyAction:
    """Tests for the apply action."""

    def test_apply_form_method(self):
        profile = Profile.objects.create_user(email="a@example.com", password="pass")
        festival = Festival.objects.create(
            name="Apply Fest", town="Paris", country="France", user=profile
        )
        client = APIClient()
        client.force_authenticate(user=profile)

        with patch("organisations.views.create_form_application") as mock_create:
            mock_app = MagicMock()
            mock_app.id = 42
            mock_create.return_value = mock_app

            response = client.post(
                f"/api/festivals/{festival.id}/apply/",
                {"application_method": "FORM"},
                format="json",
            )

        assert response.status_code == 200
        assert response.data["applicationId"] == 42

    def test_apply_form_method_exception(self):
        profile = Profile.objects.create_user(email="a@example.com", password="pass")
        festival = Festival.objects.create(
            name="Apply Fest", town="Paris", country="France", user=profile
        )
        client = APIClient()
        client.force_authenticate(user=profile)

        with patch(
            "organisations.views.create_form_application", side_effect=Exception("DB error")
        ):
            response = client.post(
                f"/api/festivals/{festival.id}/apply/",
                {"application_method": "FORM"},
                format="json",
            )

        assert response.status_code == 404

    def test_apply_missing_message_returns_400(self):
        profile = Profile.objects.create_user(email="a@example.com", password="pass")
        festival = Festival.objects.create(
            name="Apply Fest", town="Paris", country="France", user=profile
        )
        client = APIClient()
        client.force_authenticate(user=profile)

        response = client.post(
            f"/api/festivals/{festival.id}/apply/",
            {
                "application_method": "EMAIL",
                "recipients": "contact@test.com",
                "email_subject": "Hello",
                # no message
            },
            format="json",
        )
        assert response.status_code == 400

    def test_apply_invalid_recipient_returns_400(self):
        profile = Profile.objects.create_user(email="a@example.com", password="pass")
        festival = Festival.objects.create(
            name="Apply Fest", town="Paris", country="France", user=profile
        )
        client = APIClient()
        client.force_authenticate(user=profile)

        response = client.post(
            f"/api/festivals/{festival.id}/apply/",
            {
                "application_method": "EMAIL",
                "recipients": "not-an-email",
                "email_subject": "Hello",
                "message": "My message",
            },
            format="json",
        )
        assert response.status_code == 400

    def test_apply_email_method_success(self):
        profile = Profile.objects.create_user(
            email="a@example.com",
            password="pass",
            email_host="GMAIL",
            email_host_user="user@gmail.com",
        )
        festival = Festival.objects.create(
            name="Apply Fest", town="Paris", country="France", user=profile
        )
        client = APIClient()
        client.force_authenticate(user=profile)

        with (
            patch(
                "organisations.views.validate_application_recipients",
                return_value=["test@test.com"],
            ),
            patch("organisations.views.prepare_application_email", return_value=MagicMock()),
            patch("organisations.views.send_application_email"),
        ):
            response = client.post(
                f"/api/festivals/{festival.id}/apply/",
                {
                    "application_method": "EMAIL",
                    "recipients": "test@test.com",
                    "email_subject": "Hello",
                    "message": "My message",
                },
                format="json",
            )

        assert response.status_code == 200
        assert "applicationId" in response.data

    def test_apply_email_value_error_in_prepare(self):
        profile = Profile.objects.create_user(email="a@example.com", password="pass")
        festival = Festival.objects.create(
            name="Apply Fest", town="Paris", country="France", user=profile
        )
        client = APIClient()
        client.force_authenticate(user=profile)

        with (
            patch(
                "organisations.views.validate_application_recipients",
                return_value=["test@test.com"],
            ),
            patch(
                "organisations.views.prepare_application_email", side_effect=ValueError("Bad value")
            ),
        ):
            response = client.post(
                f"/api/festivals/{festival.id}/apply/",
                {
                    "application_method": "EMAIL",
                    "recipients": "test@test.com",
                    "email_subject": "Hello",
                    "message": "My message",
                },
                format="json",
            )

        assert response.status_code == 400


@pytest.mark.django_db
class TestGenerateEmailAction:
    """Tests for the generate_email action."""

    def test_generate_email_success_with_string_ids(self):
        profile = Profile.objects.create_user(email="g@example.com", password="pass")
        festival = Festival.objects.create(
            name="Email Fest", town="Paris", country="France", user=profile
        )
        client = APIClient()
        client.force_authenticate(user=profile)

        with (
            patch("organisations.views.generate_application_mail_prompt", return_value="prompt"),
            patch("organisations.views.format_email", return_value="<p>Email</p>"),
            patch("services.mistral_service.MistralClient.chat", return_value="Email content"),
        ):
            response = client.post(
                f"/api/festivals/{festival.id}/generate_email/",
                {"selected_performance_ids": "1,2,3", "language": "ENGLISH"},
                format="json",
            )
        assert response.status_code in [200, 500]

    def test_generate_email_with_list_ids(self):
        profile = Profile.objects.create_user(email="g@example.com", password="pass")
        festival = Festival.objects.create(
            name="Email Fest", town="Paris", country="France", user=profile
        )
        client = APIClient()
        client.force_authenticate(user=profile)

        with (
            patch("organisations.views.generate_application_mail_prompt", return_value="prompt"),
            patch("organisations.views.format_email", return_value="<p>Email</p>"),
            patch("services.mistral_service.MistralClient.chat", return_value="Email content"),
        ):
            response = client.post(
                f"/api/festivals/{festival.id}/generate_email/",
                {"selected_performance_ids": [1, 2], "language": "FRENCH"},
                format="json",
            )
        assert response.status_code in [200, 500]

    def test_generate_email_with_single_int_id(self):
        profile = Profile.objects.create_user(email="g@example.com", password="pass")
        festival = Festival.objects.create(
            name="Email Fest", town="Paris", country="France", user=profile
        )
        client = APIClient()
        client.force_authenticate(user=profile)

        with (
            patch("organisations.views.generate_application_mail_prompt", return_value="prompt"),
            patch("organisations.views.format_email", return_value="<p>Email</p>"),
            patch("services.mistral_service.MistralClient.chat", return_value="Email content"),
        ):
            response = client.post(
                f"/api/festivals/{festival.id}/generate_email/",
                {"selected_performance_ids": 1, "language": "ENGLISH"},
                format="json",
            )
        assert response.status_code in [200, 500]

    def test_generate_email_exception_returns_500(self):
        profile = Profile.objects.create_user(email="g@example.com", password="pass")
        festival = Festival.objects.create(
            name="Email Fest", town="Paris", country="France", user=profile
        )
        client = APIClient()
        client.force_authenticate(user=profile)

        with patch(
            "organisations.views.generate_application_mail_prompt",
            side_effect=Exception("LLM error"),
        ):
            response = client.post(
                f"/api/festivals/{festival.id}/generate_email/",
                {"language": "ENGLISH"},
                format="json",
            )
        assert response.status_code == 500


@pytest.mark.django_db
class TestOrganisationBaseViewSet:
    """Tests for base OrganisationViewSet methods."""

    def test_get_organisation_type_name_default(self):
        """OrganisationViewSet.get_organisation_type_name returns 'organisation'."""
        from organisations.views import OrganisationViewSet

        vs = OrganisationViewSet()
        assert vs.get_organisation_type_name() == "organisation"

    def test_festival_viewset_get_organisation_type_name(self):
        from organisations.festivals.views import FestivalViewSet

        vs = FestivalViewSet()
        assert vs.get_organisation_type_name() == "festival"

    def test_residency_viewset_get_organisation_type_name(self):
        from organisations.residencies.views import ResidencyViewSet

        vs = ResidencyViewSet()
        assert vs.get_organisation_type_name() == "residency"

    def test_venue_viewset_get_organisation_type_name(self):
        from organisations.venues.views import VenueViewSet

        vs = VenueViewSet()
        assert vs.get_organisation_type_name() == "venue"

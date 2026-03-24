from datetime import date, datetime
from unittest.mock import Mock, patch

import pytest
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient

from applications.models import Application
from organisations.festivals.models import Festival
from performances.models import Performance
from profiles.models import Profile


@pytest.fixture
def api_client():
    """Fixture to provide an API client"""
    return APIClient()


@pytest.fixture
def festival(db, profile):
    """Fixture to create a test festival"""
    return Festival.objects.create(
        name="Tst Festival",
        description="Tst Description",
        country="France",
        town="Paris",
        festival_type="STREET",
        website_url="https://festival.com",
        start_date=date(2025, 7, 15),
        end_date=date(2025, 7, 20),
        application_type="EMAIL",
        user=profile,
    )


@pytest.fixture
def profile(db):
    """Fixture to create a test profile with id=2 (used by views)"""
    # Delete any existing profile with id=2 first
    Profile.objects.filter(id=2).delete()

    profile = Profile(
        id=2,
        email="test@example.com",
        first_name="Test",
        last_name="User",
        email_host="GMAIL",
        email_host_user="test@gmail.com",
    )
    profile.set_password("testpass123")
    profile.save()
    return profile


@pytest.fixture
def performance(profile):
    """Fixture to create a test performance"""
    return Performance.objects.create(performance_title="Test Performance", profile=profile)


@pytest.fixture(autouse=True)
def authenticate_api_client(api_client, profile):
    """Automatically authenticate the API client for all tests"""
    api_client.force_authenticate(user=profile)


@pytest.fixture
def mock_email():
    """Fixture to provide a properly configured email mock"""
    with patch("django.core.mail.EmailMultiAlternatives") as mock:
        mock_instance = Mock()
        mock_instance.send.return_value = 1  # Simulate successful send
        mock_instance.attach_alternative = Mock()
        mock_instance.attach = Mock()
        mock.return_value = mock_instance
        yield mock


@pytest.mark.django_db
class TestFestivalViewSet:
    """Test cases for FestivalViewSet"""

    def test_list_festivals(self, api_client, festival):
        """Test listing all festivals"""
        response = api_client.get("/api/festivals/")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 1
        assert len(response.data["results"]) == 1
        assert response.data["results"][0]["name"] == "Tst Festival"

    def test_create_festival(self, api_client):
        """Test creating a new festival"""
        data = {
            "name": "New Festival",
            "country": "Spain",
            "town": "Barcelona",
            "festival_type": "CIRCUS",
        }

        response = api_client.post("/api/festivals/", data)

        assert response.status_code == status.HTTP_201_CREATED
        assert Festival.objects.count() == 1
        assert Festival.objects.first().name == "New Festival"

    def test_retrieve_festival(self, api_client, festival):
        """Test retrieving a specific festival"""
        response = api_client.get(f"/api/festivals/{festival.id}/")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["name"] == "Tst Festival"
        assert response.data["country"] == "France"

    def test_update_festival(self, api_client, festival):
        """Test updating a festival"""
        data = {
            "name": "Updated Festival",
            "country": "Germany",
            "town": "Berlin",
        }

        response = api_client.patch(f"/api/festivals/{festival.id}/", data)

        assert response.status_code == status.HTTP_200_OK
        festival.refresh_from_db()
        assert festival.name == "Updated Festival"
        assert festival.country == "Germany"

    def test_delete_festival(self, api_client, festival):
        """Test deleting a festival"""
        festival_id = festival.id
        response = api_client.delete(f"/api/festivals/{festival_id}/")

        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not Festival.objects.filter(id=festival_id).exists()


@pytest.mark.django_db
class TestFestivalEnrichAction:
    """Test cases for the enrich action"""

    @patch("organisations.views.MistralClient")
    def test_enrich_festival_success(self, mock_mistral_client, api_client, festival):
        """Test enriching a festival with LLM data"""
        from mistralai import TextChunk

        # Mock the Mistral client
        mock_mistral = Mock()

        # Mock search response with proper ConversationResponse structure
        mock_text_chunk = Mock(spec=TextChunk, text="Search results about the festival")
        mock_output = Mock(type="message.output", content=[mock_text_chunk])
        mock_search_response = Mock(outputs=[mock_output])
        mock_mistral.search.return_value = mock_search_response

        mock_mistral.chat.return_value = """
        {
            "description": "Enriched description",
            "start_date": "2025-07-15",
            "end_date": "2025-07-20"
        }
        """
        mock_mistral_client.return_value = mock_mistral

        response = api_client.get(f"/api/festivals/{festival.id}/enrich/")

        assert response.status_code == status.HTTP_200_OK
        assert mock_mistral.search.called
        assert mock_mistral.chat.called

    @patch("organisations.views.MistralClient")
    def test_enrich_festival_not_found(self, mock_mistral_client, api_client):
        """Test enriching a non-existent festival"""
        response = api_client.get("/api/festivals/9999/enrich/")

        assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
class TestFestivalGenerateEmailAction:
    """Test cases for the generate_email action"""

    @patch("organisations.views.MistralClient")
    def test_generate_email_without_performances(
        self, mock_mistral_client, api_client, festival, profile
    ):
        """Test generating email without performances"""
        mock_mistral = Mock()
        mock_mistral.chat.return_value = "Generated email content"
        mock_mistral_client.return_value = mock_mistral

        response = api_client.post(f"/api/festivals/{festival.id}/generate_email/", {})

        assert response.status_code == status.HTTP_200_OK
        assert "message" in response.data
        assert response.data["message"] == "Generated email content"

    @patch("organisations.views.MistralClient")
    def test_generate_email_with_performances(
        self, mock_mistral_client, api_client, festival, profile, performance
    ):
        """Test generating email with selected performances"""
        mock_mistral = Mock()
        mock_mistral.chat.return_value = "Generated email with performances"
        mock_mistral_client.return_value = mock_mistral

        data = {"selected_performance_ids": [str(performance.id)]}

        response = api_client.post(f"/api/festivals/{festival.id}/generate_email/", data)

        assert response.status_code == status.HTTP_200_OK
        assert "message" in response.data

    @patch("organisations.views.MistralClient")
    def test_generate_email_with_multiple_performances(
        self, mock_mistral_client, api_client, festival, profile
    ):
        """Test generating email with multiple performances"""
        performance1 = Performance.objects.create(performance_title="Show 1", profile=profile)
        performance2 = Performance.objects.create(performance_title="Show 2", profile=profile)

        mock_mistral = Mock()
        mock_mistral.chat.return_value = "Generated email"
        mock_mistral_client.return_value = mock_mistral

        data = {"selected_performance_ids": f"{performance1.id},{performance2.id}"}

        response = api_client.post(f"/api/festivals/{festival.id}/generate_email/", data)

        assert response.status_code == status.HTTP_200_OK

    @patch("organisations.views.MistralClient")
    def test_generate_email_festival_not_found(self, mock_mistral_client, api_client):
        """Test generating email for non-existent festival"""
        response = api_client.post("/api/festivals/9999/generate_email/", {})

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "error" in response.data


@pytest.mark.django_db(transaction=True)
class TestFestivalApplyAction:
    """Test cases for the apply action"""

    def test_apply_missing_required_fields(self, api_client, festival, profile):
        """Test applying without required fields"""
        response = api_client.post(f"/api/festivals/{festival.id}/apply/", {})

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "error" in response.data

    def test_apply_festival_not_found(self, api_client, profile):
        """Test applying to non-existent festival"""
        data = {
            "message": "Test message",
            "email_subject": "Test Subject",
            "recipients": "test@example.com",
        }

        response = api_client.post("/api/festivals/9999/apply/", data)

        assert response.status_code == status.HTTP_404_NOT_FOUND

    @patch("profiles.emails.get_user_email_connection")
    @patch("organisations.services.EmailMultiAlternatives")
    def test_apply_creates_application(
        self, mock_email, mock_connection, api_client, festival, profile
    ):
        """Test that applying creates an application"""
        mock_connection.return_value = Mock()
        mock_email_instance = Mock()
        mock_email_instance.send.return_value = 1
        mock_email.return_value = mock_email_instance

        data = {
            "message": "<p>Test application message</p>",
            "email_subject": "Application to Test Festival",
            "recipients": "festival@example.com",
        }

        response = api_client.post(f"/api/festivals/{festival.id}/apply/", data)

        assert response.status_code == status.HTTP_200_OK
        assert Application.objects.count() == 1

        application = Application.objects.first()
        assert application.organisation == festival
        assert application.message == "<p>Test application message</p>"
        assert application.email_subject == "Application to Test Festival"
        assert application.status == "APPLIED"

    @patch("profiles.emails.get_user_email_connection")
    @patch("organisations.services.EmailMultiAlternatives")
    def test_apply_with_performances(
        self, mock_email, mock_connection, api_client, festival, profile, performance
    ):
        """Test applying with performances attached"""
        mock_connection.return_value = Mock()
        mock_email_instance = Mock()
        mock_email_instance.send.return_value = 1
        mock_email.return_value = mock_email_instance
        print("PERFORMANCE", performance, "ID: ", performance.id)
        data = {
            "message": "<p>Test message</p>",
            "email_subject": "Test Subject",
            "performances": [str(performance.id)],
            "recipients": "festival@example.com",
        }

        response = api_client.post(f"/api/festivals/{festival.id}/apply/", data)

        assert response.status_code == status.HTTP_200_OK
        application = Application.objects.first()
        print("PERF: ", application.performances, response)
        assert application.performances.count() == 1

    @patch("profiles.emails.get_user_email_connection")
    @patch("organisations.services.EmailMultiAlternatives")
    def test_apply_duplicate_application_same_year(
        self, mock_email, mock_connection, api_client, festival, profile
    ):
        """Test that duplicate applications for the same year are rejected"""
        mock_connection.return_value = Mock()
        mock_email_instance = Mock()
        mock_email_instance.send.return_value = 1
        mock_email.return_value = mock_email_instance

        # Create first application
        Application.objects.create(
            organisation=festival,
            application_date=timezone.now().date(),
            status="APPLIED",
            message="First application",
            email_subject="First Subject",
            profile=profile,
        )

        # Try to create second application
        data = {
            "message": "<p>Second application</p>",
            "email_subject": "Second Subject",
            "recipients": "festival@example.com",
        }

        response = api_client.post(f"/api/festivals/{festival.id}/apply/", data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "already exists" in response.data

    @patch("profiles.emails.get_user_email_connection")
    @patch("organisations.services.EmailMultiAlternatives")
    def test_apply_email_sending_failure(
        self, mock_email, mock_connection, api_client, festival, profile
    ):
        """Test handling of email sending failure"""
        mock_connection.return_value = Mock()
        mock_email_instance = Mock()
        mock_email_instance.send.side_effect = Exception("Email server error")
        mock_email.return_value = mock_email_instance

        data = {
            "message": "<p>Test message</p>",
            "email_subject": "Test Subject",
            "recipients": "festival@example.com",
        }

        response = api_client.post(f"/api/festivals/{festival.id}/apply/", data)

        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert "Email failed to send" in response.data["error"]

    @patch("profiles.emails.get_user_email_connection")
    @patch("organisations.services.EmailMultiAlternatives")
    def test_apply_calculates_correct_application_year(
        self, mock_email, mock_connection, api_client, festival, profile
    ):
        """Test that application year uses profile.current_application_year or defaults to current year"""
        mock_connection.return_value = Mock()
        mock_email_instance = Mock()
        mock_email_instance.send.return_value = 1
        mock_email.return_value = mock_email_instance

        data = {
            "message": "<p>Test message</p>",
            "email_subject": "Test Subject",
            "recipients": "festival@example.com",
        }

        with patch("django.utils.timezone.now") as mock_now:
            # When current_application_year is None, defaults to current year
            mock_now.return_value = timezone.make_aware(datetime(2025, 10, 1))
            profile.current_application_year = None
            profile.save()

            response = api_client.post(f"/api/festivals/{festival.id}/apply/", data)

            assert response.status_code == status.HTTP_200_OK
            application = Application.objects.first()
            # Should use current year from timezone.now() = 2025
            assert application.application_year == 2025

    @patch("profiles.emails.get_user_email_connection")
    @patch("organisations.services.EmailMultiAlternatives")
    def test_apply_uses_profile_current_application_year(
        self, mock_email, mock_connection, api_client, profile
    ):
        """Test that application year from profile.current_application_year is used for deduplication"""
        mock_connection.return_value = Mock()
        mock_email_instance = Mock()
        mock_email_instance.send.return_value = 1
        mock_email.return_value = mock_email_instance

        # Create a non-test festival to ensure duplicate check isn't bypassed
        festival = Festival.objects.create(
            name="Real Festival",
            description="Not a test",
            country="France",
            town="Paris",
            festival_type="STREET",
            website_url="https://festival.com",
            start_date=date(2025, 7, 15),
            end_date=date(2025, 7, 20),
            application_type="EMAIL",
            user=profile,
        )

        # Set current_application_year on profile to 2027
        profile.current_application_year = 2027
        profile.save()

        data = {
            "message": "<p>Test message</p>",
            "email_subject": "Test Subject",
            "recipients": "festival@example.com",
        }

        # First application should succeed
        response = api_client.post(f"/api/festivals/{festival.id}/apply/", data)
        assert response.status_code == status.HTTP_200_OK
        assert Application.objects.count() == 1

        # Second application in same year should fail (duplicate)
        response = api_client.post(f"/api/festivals/{festival.id}/apply/", data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "already exists" in str(response.data)

    @patch("profiles.emails.get_user_email_connection")
    @patch("organisations.services.EmailMultiAlternatives")
    def test_apply_defaults_to_current_year_when_not_set(
        self, mock_email, mock_connection, api_client, profile
    ):
        """Test that application year defaults to current calendar year when profile.current_application_year is None"""
        mock_connection.return_value = Mock()
        mock_email_instance = Mock()
        mock_email_instance.send.return_value = 1
        mock_email.return_value = mock_email_instance

        # Create a non-test festival
        festival = Festival.objects.create(
            name="Summer Music Festival",
            description="A real festival",
            country="France",
            town="Paris",
            festival_type="STREET",
            website_url="https://festival.com",
            start_date=date(2025, 7, 15),
            end_date=date(2025, 7, 20),
            application_type="EMAIL",
            user=profile,
        )

        # Ensure current_application_year is None
        profile.current_application_year = None
        profile.save()

        data = {
            "message": "<p>Test message</p>",
            "email_subject": "Test Subject",
            "recipients": "festival@example.com",
        }

        with patch("django.utils.timezone.now") as mock_now:
            # May 15, 2025 -> application_year should be 2025 (before Sept)
            mock_now.return_value = timezone.make_aware(datetime(2025, 5, 15))

            response = api_client.post(f"/api/festivals/{festival.id}/apply/", data)

            assert response.status_code == status.HTTP_200_OK
            # Two applications can exist if they have different application years
            # Application created on May 15, 2025 will have application_year of 2025
            application = Application.objects.first()
            assert application.application_year == 2025

    @patch("profiles.emails.get_user_email_connection")
    @patch("organisations.services.EmailMultiAlternatives")
    def test_apply_with_different_application_years(
        self, mock_email, mock_connection, api_client, profile
    ):
        """Test that multiple applications in different years can both exist"""
        mock_connection.return_value = Mock()
        mock_email_instance = Mock()
        mock_email_instance.send.return_value = 1
        mock_email.return_value = mock_email_instance

        # Create a non-test festival
        festival = Festival.objects.create(
            name="Annual Music Festival",
            description="A real festival",
            country="France",
            town="Paris",
            festival_type="STREET",
            website_url="https://festival.com",
            start_date=date(2025, 7, 15),
            end_date=date(2025, 7, 20),
            application_type="EMAIL",
            user=profile,
        )

        data = {
            "message": "<p>Test message</p>",
            "email_subject": "Test Subject",
            "recipients": "festival@example.com",
        }

        # First application in year 2025
        profile.current_application_year = 2025
        profile.save()

        with patch("django.utils.timezone.now") as mock_now:
            mock_now.return_value = timezone.make_aware(datetime(2025, 5, 15))
            response1 = api_client.post(f"/api/festivals/{festival.id}/apply/", data)
            assert response1.status_code == status.HTTP_200_OK

        # Second application in year 2026
        profile.current_application_year = 2026
        profile.save()

        with patch("django.utils.timezone.now") as mock_now:
            mock_now.return_value = timezone.make_aware(datetime(2026, 5, 15))
            response2 = api_client.post(f"/api/festivals/{festival.id}/apply/", data)
            assert response2.status_code == status.HTTP_200_OK

        assert Application.objects.count() == 2
        apps = list(Application.objects.all().order_by("application_year_value"))
        assert apps[0].application_year == 2025
        assert apps[1].application_year == 2026

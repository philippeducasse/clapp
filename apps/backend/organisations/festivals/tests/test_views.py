import pytest
from datetime import date, datetime
from unittest.mock import Mock, patch
from django.utils import timezone
from rest_framework.test import APIClient
from rest_framework import status
from organisations.festivals.models import Festival
from applications.models import Application
from profiles.models import Profile
from performances.models import Performance


@pytest.fixture
def api_client():
    """Fixture to provide an API client"""
    return APIClient()


@pytest.fixture
def festival():
    """Fixture to create a test festival"""
    return Festival.objects.create(
        festival_name="Test Festival",
        description="Test Description",
        country="France",
        town="Paris",
        festival_type="STREET",
        website_url="https://testfestival.com",
        contact_email="contact@testfestival.com",
        contact_person="John Doe",
        start_date=date(2025, 7, 15),
        end_date=date(2025, 7, 20),
        application_type="EMAIL",
    )


@pytest.fixture
def profile(db):
    """Fixture to create a test profile with id=2 (used by views)"""
    # Delete any existing profile with id=2 first
    Profile.objects.filter(id=2).delete()

    profile = Profile(
        id=2, email="test@example.com", first_name="Test", last_name="User"
    )
    profile.set_password("testpass123")
    profile.save()
    return profile


@pytest.fixture
def performance(profile):
    """Fixture to create a test performance"""
    return Performance.objects.create(
        performance_title="Test Performance", profile=profile
    )


@pytest.mark.django_db
class TestFestivalViewSet:
    """Test cases for FestivalViewSet"""

    def test_list_festivals(self, api_client, festival):
        """Test listing all festivals"""
        response = api_client.get("/api/festivals/")

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert response.data[0]["festival_name"] == "Test Festival"

    def test_create_festival(self, api_client):
        """Test creating a new festival"""
        data = {
            "festival_name": "New Festival",
            "country": "Spain",
            "town": "Barcelona",
            "festival_type": "CIRCUS",
        }

        response = api_client.post("/api/festivals/", data)

        assert response.status_code == status.HTTP_201_CREATED
        assert Festival.objects.count() == 1
        assert Festival.objects.first().festival_name == "New Festival"

    def test_retrieve_festival(self, api_client, festival):
        """Test retrieving a specific festival"""
        response = api_client.get(f"/api/festivals/{festival.id}/")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["festival_name"] == "Test Festival"
        assert response.data["country"] == "France"

    def test_update_festival(self, api_client, festival):
        """Test updating a festival"""
        data = {
            "festival_name": "Updated Festival",
            "country": "Germany",
            "town": "Berlin",
        }

        response = api_client.patch(f"/api/festivals/{festival.id}/", data)

        assert response.status_code == status.HTTP_200_OK
        festival.refresh_from_db()
        assert festival.festival_name == "Updated Festival"
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

    @patch("festivals.views.MistralClient")
    @patch("festivals.views.GeminiClient")
    def test_enrich_festival_success(
        self, mock_gemini_client, mock_mistral_client, api_client, festival
    ):
        """Test enriching a festival with LLM data"""
        # Mock the clients
        mock_gemini = Mock()
        mock_gemini.search.return_value = "Search results about the festival"
        mock_gemini_client.return_value = mock_gemini

        mock_mistral = Mock()
        mock_mistral.chat.return_value = """
        {
            "description": "Enriched description",
            "contact_person": "Jane Smith",
            "start_date": "2025-07-15",
            "end_date": "2025-07-20"
        }
        """
        mock_mistral_client.return_value = mock_mistral

        response = api_client.get(f"/api/festivals/{festival.id}/enrich/")

        assert response.status_code == status.HTTP_200_OK
        assert mock_gemini.search.called
        assert mock_mistral.chat.called

    @patch("festivals.views.MistralClient")
    @patch("festivals.views.GeminiClient")
    def test_enrich_festival_not_found(
        self, mock_gemini_client, mock_mistral_client, api_client
    ):
        """Test enriching a non-existent festival"""
        response = api_client.get("/api/festivals/9999/enrich/")

        assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
class TestFestivalGenerateEmailAction:
    """Test cases for the generate_email action"""

    @patch("festivals.views.MistralClient")
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

    @patch("festivals.views.MistralClient")
    def test_generate_email_with_performances(
        self, mock_mistral_client, api_client, festival, profile, performance
    ):
        """Test generating email with selected performances"""
        mock_mistral = Mock()
        mock_mistral.chat.return_value = "Generated email with performances"
        mock_mistral_client.return_value = mock_mistral

        data = {"selected_performance_ids": str(performance.id)}

        response = api_client.post(
            f"/api/festivals/{festival.id}/generate_email/", data
        )

        assert response.status_code == status.HTTP_200_OK
        assert "message" in response.data

    @patch("festivals.views.MistralClient")
    def test_generate_email_with_multiple_performances(
        self, mock_mistral_client, api_client, festival, profile
    ):
        """Test generating email with multiple performances"""
        performance1 = Performance.objects.create(
            performance_title="Show 1", profile=profile
        )
        performance2 = Performance.objects.create(
            performance_title="Show 2", profile=profile
        )

        mock_mistral = Mock()
        mock_mistral.chat.return_value = "Generated email"
        mock_mistral_client.return_value = mock_mistral

        data = {"selected_performance_ids": f"{performance1.id},{performance2.id}"}

        response = api_client.post(
            f"/api/festivals/{festival.id}/generate_email/", data
        )

        assert response.status_code == status.HTTP_200_OK

    @patch("festivals.views.MistralClient")
    def test_generate_email_festival_not_found(self, mock_mistral_client, api_client):
        """Test generating email for non-existent festival"""
        response = api_client.post("/api/festivals/9999/generate_email/", {})

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "error" in response.data


@pytest.mark.django_db
class TestFestivalApplyAction:
    """Test cases for the apply action"""

    def test_apply_missing_required_fields(self, api_client, festival, profile):
        """Test applying without required fields"""
        response = api_client.post(f"/api/festivals/{festival.id}/apply/", {})

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "error" in response.data

    def test_apply_festival_not_found(self, api_client, profile):
        """Test applying to non-existent festival"""
        data = {"message": "Test message", "email_subject": "Test Subject"}

        response = api_client.post("/api/festivals/9999/apply/", data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    @patch("festivals.views.EmailMultiAlternatives")
    def test_apply_creates_application(self, mock_email, api_client, festival, profile):
        """Test that applying creates an application"""
        mock_email_instance = Mock()
        mock_email.return_value = mock_email_instance

        data = {
            "message": "<p>Test application message</p>",
            "email_subject": "Application to Test Festival",
        }

        response = api_client.post(f"/api/festivals/{festival.id}/apply/", data)

        assert response.status_code == status.HTTP_200_OK
        assert Application.objects.count() == 1

        application = Application.objects.first()
        assert application.festival == festival
        assert application.message == "<p>Test application message</p>"
        assert application.email_subject == "Application to Test Festival"
        assert application.application_status == "APPLIED"

    @patch("festivals.views.EmailMultiAlternatives")
    def test_apply_with_performances(
        self, mock_email, api_client, festival, profile, performance
    ):
        """Test applying with performances attached"""
        mock_email_instance = Mock()
        mock_email.return_value = mock_email_instance

        data = {
            "message": "<p>Test message</p>",
            "email_subject": "Test Subject",
            "performances": str(performance.id),
        }

        response = api_client.post(f"/api/festivals/{festival.id}/apply/", data)

        assert response.status_code == status.HTTP_200_OK
        application = Application.objects.first()
        assert application.performances.count() == 1

    @patch("festivals.views.EmailMultiAlternatives")
    def test_apply_duplicate_application_same_year(
        self, mock_email, api_client, festival, profile
    ):
        """Test that duplicate applications for the same year are rejected"""
        mock_email_instance = Mock()
        mock_email.return_value = mock_email_instance

        # Create first application
        Application.objects.create(
            festival=festival,
            application_date=timezone.now().date(),
            application_status="APPLIED",
            message="First application",
            email_subject="First Subject",
            profile=profile,
        )

        # Try to create second application
        data = {
            "message": "<p>Second application</p>",
            "email_subject": "Second Subject",
        }

        response = api_client.post(f"/api/festivals/{festival.id}/apply/", data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "already exists" in response.data

    @patch("festivals.views.EmailMultiAlternatives")
    def test_apply_email_sending_failure(
        self, mock_email, api_client, festival, profile
    ):
        """Test handling of email sending failure"""
        mock_email_instance = Mock()
        mock_email_instance.send.side_effect = Exception("Email server error")
        mock_email.return_value = mock_email_instance

        data = {"message": "<p>Test message</p>", "email_subject": "Test Subject"}

        response = api_client.post(f"/api/festivals/{festival.id}/apply/", data)

        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert "Email failed to send" in response.data["error"]

    @patch("festivals.views.EmailMultiAlternatives")
    def test_apply_calculates_correct_application_year(
        self, mock_email, api_client, festival, profile
    ):
        """Test that application year is calculated correctly"""
        mock_email_instance = Mock()
        mock_email.return_value = mock_email_instance

        data = {"message": "<p>Test message</p>", "email_subject": "Test Subject"}

        with patch("django.utils.timezone.now") as mock_now:
            # Test for October (should increment year)
            mock_now.return_value = timezone.make_aware(datetime(2025, 10, 1))

            response = api_client.post(f"/api/festivals/{festival.id}/apply/", data)

            assert response.status_code == status.HTTP_200_OK
            application = Application.objects.first()
            assert application.application_year == 2026

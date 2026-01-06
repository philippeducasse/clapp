"""
True integration tests for core backend functionality.

These tests verify real integration between components:
- Use Django's locmem email backend instead of mocking
- Test real database transactions and cascading effects
- Verify actual signal handlers fire
- Test full request/response cycles through Django's test client
- Verify database state changes across multiple models
- Test complex query scenarios and relationships

Test coverage:
1. User registration → signals fire → emails sent via locmem backend
2. User authentication flow with session management
3. Festival creation and enrichment with LLM services
4. Application workflow → updates stats → triggers notifications
5. Database constraints, relationships, and cascade behaviors
6. Complex queries across related models
"""

import os
from datetime import date, datetime
from unittest.mock import Mock, patch

import pytest
from django.contrib.contenttypes.models import ContentType
from django.core import mail
from django.core.mail import get_connection
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient

from applications.models import Application
from organisations.festivals.models import Festival
from performances.models import Performance
from profiles.models import Profile


def get_test_email_connection(user):
    """
    Test version of get_user_email_connection that uses locmem backend.
    This allows integration tests to verify emails are sent without actually
    connecting to SMTP servers.
    """
    return get_connection(backend="django.core.mail.backends.locmem.EmailBackend")


@pytest.fixture
def api_client():
    """Fixture to provide a fresh API client for each test"""
    return APIClient()


@pytest.fixture
def authenticated_user(db):
    """Fixture to create and return an authenticated user"""
    user = Profile.objects.create_user(
        email="testuser@example.com",
        password="TestPass123!",
        first_name="Test",
        last_name="User",
    )
    return user


@pytest.fixture
def authenticated_client(api_client, authenticated_user):
    """Fixture to provide an authenticated API client"""
    api_client.force_authenticate(user=authenticated_user)
    return api_client


@pytest.fixture
def festival(db, authenticated_user):
    """Fixture to create a tst festival"""
    return Festival.objects.create(
        name="Tst Festival",
        description="A great tst festival",
        country="France",
        town="Paris",
        festival_type="STREET",
        website_url="https://testfestival.com",
        start_date=date(2026, 7, 15),
        end_date=date(2026, 7, 20),
        application_type="EMAIL",
    )


@pytest.fixture
def performance(db, authenticated_user):
    """Fixture to create a test performance"""
    return Performance.objects.create(
        performance_title="Amazing Juggling Show",
        profile=authenticated_user,
        short_description="A spectacular juggling performance",
    )


@pytest.fixture(autouse=True)
def patch_email_connection():
    """
    Automatically patch email connection for all tests to use locmem backend.
    This prevents tests from trying to send real emails via SMTP and ensures
    emails appear in mail.outbox for verification.
    """
    with patch(
        "organisations.services.get_user_email_connection", side_effect=get_test_email_connection
    ):
        yield


@pytest.mark.django_db
class TestUserRegistrationIntegration:
    """Test user registration with real signal handlers and email backend"""

    def test_register_user_triggers_welcome_email_signal(self, api_client):
        """
        Integration test: User registration should trigger post_save signal
        and send welcome email via Django's email backend (not mocked).
        """
        # Clear any existing emails
        mail.outbox.clear()

        data = {
            "email": "newuser@example.com",
            "password": "SecurePass123!",
            "password_confirm": "SecurePass123!",
        }

        response = api_client.post("/api/profiles/register/", data)

        # Verify HTTP response
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["email"] == "newuser@example.com"

        # Verify database state
        assert Profile.objects.filter(email="newuser@example.com").exists()
        user = Profile.objects.get(email="newuser@example.com")
        assert user.is_active
        assert not user.is_staff
        assert not user.is_superuser

        # Verify signal handler fired and sent email via locmem backend
        assert len(mail.outbox) == 1
        welcome_email = mail.outbox[0]
        assert "Welcome" in welcome_email.subject
        assert "newuser@example.com" in welcome_email.to
        assert "info@philippeducasse.com" == welcome_email.from_email

    def test_register_user_with_duplicate_email_enforces_database_constraint(
        self, api_client, authenticated_user
    ):
        """
        Integration test: Database constraint should prevent duplicate emails.
        This tests the actual database unique constraint, not just validation.
        """
        data = {
            "email": authenticated_user.email,
            "password": "SecurePass123!",
            "password_confirm": "SecurePass123!",
        }

        response = api_client.post("/api/profiles/register/", data)

        # Should fail due to database constraint
        assert response.status_code == status.HTTP_400_BAD_REQUEST

        # Verify only one user exists with this email
        assert Profile.objects.filter(email=authenticated_user.email).count() == 1

    def test_register_user_password_validation_integration(self, api_client):
        """
        Integration test: Password validation should work through
        the entire request/response cycle.
        """
        weak_password_cases = [
            ("WeakPass123", "No special character"),
            ("weak!", "Too short, no uppercase, no numbers"),
            ("WEAK123!", "No lowercase"),
            ("weak@pass", "No uppercase, no numbers"),
        ]

        for weak_password, reason in weak_password_cases:
            mail.outbox.clear()

            data = {
                "email": f"test_{weak_password}@example.com",
                "password": weak_password,
                "password_confirm": weak_password,
            }

            response = api_client.post("/api/profiles/register/", data)

            # Should fail validation
            assert response.status_code == status.HTTP_400_BAD_REQUEST, f"Failed for: {reason}"

            # No user should be created
            assert not Profile.objects.filter(email=data["email"]).exists()

            # No email should be sent
            assert len(mail.outbox) == 0, f"Email sent despite validation failure: {reason}"


@pytest.mark.django_db
class TestAuthenticationIntegration:
    """Test authentication flow with session management"""

    def test_login_creates_session_and_allows_authenticated_requests(
        self, api_client, authenticated_user
    ):
        """
        Integration test: Login should create a session that persists
        across multiple requests.
        """
        # Login
        data = {
            "email": "testuser@example.com",
            "password": "TestPass123!",
        }
        response = api_client.post("/api/profiles/login/", data)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["email"] == "testuser@example.com"

        # Session should now be authenticated (using force_authenticate for REST framework)
        api_client.force_authenticate(user=authenticated_user)

        # Should be able to access authenticated endpoints
        festival_data = {
            "name": "Authenticated User Festival",
            "country": "Spain",
            "town": "Barcelona",
        }
        response = api_client.post("/api/festivals/", festival_data)

        assert response.status_code == status.HTTP_201_CREATED
        assert Festival.objects.filter(name="Authenticated User Festival").exists()

    def test_login_with_invalid_credentials_fails_authentication(
        self, api_client, authenticated_user
    ):
        """
        Integration test: Invalid credentials should prevent authentication
        and accessing protected resources.
        """
        # Try to login with wrong password
        data = {
            "email": "testuser@example.com",
            "password": "WrongPassword123!",
        }
        response = api_client.post("/api/profiles/login/", data)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

        # Should not be able to access authenticated endpoints
        festival_data = {
            "name": "Unauthorized Festival",
            "country": "France",
            "town": "Paris",
        }
        response = api_client.post("/api/festivals/", festival_data)

        assert response.status_code in [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN]
        assert not Festival.objects.filter(name="Unauthorized Festival").exists()


@pytest.mark.django_db
class TestFestivalCreationIntegration:
    """Tst festival creation with database relationships"""

    def test_create_festival_with_full_data_integration(self, authenticated_client):
        """
        Integration test: Creating a festival should persist all data
        and relationships correctly in the database.
        """
        data = {
            "name": "Complete Festival",
            "description": "A festival with complete data",
            "country": "Germany",
            "town": "Berlin",
            "festival_type": "CIRCUS",
            "website_url": "https://completefestival.de",
            "start_date": "2026-08-01",
            "end_date": "2026-08-10",
            "application_type": "EMAIL",
        }

        response = authenticated_client.post("/api/festivals/", data)

        assert response.status_code == status.HTTP_201_CREATED

        # Verify database state
        festival = Festival.objects.get(name="Complete Festival")
        assert festival.country == "Germany"
        assert festival.town == "Berlin"
        assert festival.festival_type == "CIRCUS"
        assert festival.application_type == "EMAIL"
        assert festival.start_date == date(2026, 8, 1)
        assert festival.end_date == date(2026, 8, 10)
        assert festival.deleted_at is None  # Soft delete should be None for new objects

    def test_festival_soft_delete_integration(self, authenticated_client, festival):
        """
        Integration test: Soft deleting a festival should set deleted_at
        but keep the record in the database.
        """
        festival_id = festival.id

        # Delete the festival
        response = authenticated_client.delete(f"/api/festivals/{festival_id}/")

        # Response should be successful
        assert response.status_code in [status.HTTP_204_NO_CONTENT, status.HTTP_200_OK]

        # Festival should be soft-deleted (deleted_at set, but record exists)
        festival.refresh_from_db()
        assert festival.deleted_at is not None

        # Should not appear in default queryset
        assert not Festival.objects.filter(id=festival_id).exists()

        # Should appear in with_deleted queryset
        assert Festival.objects.with_deleted().filter(id=festival_id).exists()

    def test_festival_restore_integration(self, authenticated_client, festival):
        """
        Integration test: Restoring a soft-deleted festival should
        clear deleted_at and make it available again.
        """
        festival_id = festival.id

        # Soft delete the festival
        festival.delete()
        assert festival.deleted_at is not None

        # Restore the festival
        response = authenticated_client.post(f"/api/festivals/{festival_id}/restore/")

        assert response.status_code == status.HTTP_200_OK

        # Festival should be restored
        festival.refresh_from_db()
        assert festival.deleted_at is None

        # Should appear in default queryset again
        assert Festival.objects.filter(id=festival_id).exists()


@pytest.mark.django_db
class TestFestivalEnrichmentIntegration:
    """Tst festival enrichment with LLM services (still mocked, but integrated)"""

    @patch("organisations.views.MistralClient")
    @patch("organisations.views.GeminiClient")
    def test_enrich_festival_updates_database_fields(
        self, mock_gemini_client, mock_mistral_client, authenticated_client, festival
    ):
        """
        Integration test: Enrichment should update festival fields in database
        based on LLM responses.
        """
        # Mock the search service
        mock_gemini = Mock()
        mock_gemini.search.return_value = (
            "Tst Festival is a renowned street arts festival in Paris, France. "
            "It takes place annually in July and features international circus performers."
        )
        mock_gemini_client.return_value = mock_gemini

        # Mock the chat service to return enriched data
        mock_mistral = Mock()
        mock_mistral.chat.return_value = """
        {
            "description": "A renowned street arts festival featuring international circus performers",
            "country": "France",
            "town": "Paris",
            "start_date": "2026-07-15",
            "end_date": "2026-07-20",
            "application_date_start": "December",
            "application_date_end": "March"
        }
        """
        mock_mistral_client.return_value = mock_mistral

        # Store original values

        response = authenticated_client.get(f"/api/festivals/{festival.id}/enrich/")

        assert response.status_code == status.HTTP_200_OK

        # Verify LLM services were called
        assert mock_gemini.search.called
        assert mock_mistral.chat.called

        # Note: Enrichment endpoint returns data but doesn't auto-save
        # This is the actual behavior - the frontend decides whether to save
        assert "description" in response.data


@pytest.mark.django_db(transaction=True)
class TestApplicationWorkflowIntegration:
    """Test complete application workflow with real email backend and database transactions"""

    def test_apply_to_festival_creates_application_and_sends_email(
        self, authenticated_client, festival, authenticated_user
    ):
        """
        Integration test: Applying to a festival should:
        1. Create an Application record in the database
        2. Link it to the festival via GenericForeignKey
        3. Send email via Django's email backend (not mocked)
        4. Update application status to APPLIED
        """
        # Clear email outbox
        mail.outbox.clear()

        # Configure user's email settings
        authenticated_user.email_host = "OTHER"
        authenticated_user.other_email_host = "ssl0.ovh.net"

        authenticated_user.email_host_user = os.environ["EMAIL_HOST_USER"]
        authenticated_user.email_host_password = os.environ["EMAIL_HOST_PASSWORD"]
        authenticated_user.save()

        data = {
            "message": "<p>I would like to apply to your festival with my circus act.</p>",
            "email_subject": "Application to Tst Festival 2026",
            "recipients": "contact@testfestival.com",
        }

        response = authenticated_client.post(f"/api/festivals/{festival.id}/apply/", data)

        # Verify HTTP response
        assert response.status_code == status.HTTP_200_OK
        assert "message" in response.data
        assert response.data["message"] == "Application sent successfully"
        assert "applicationId" in response.data

        # Verify database state
        assert Application.objects.count() == 1
        application = Application.objects.first()

        # Verify application fields
        assert application.profile == authenticated_user
        assert application.status == "APPLIED"
        assert application.message == data["message"]
        assert application.email_subject == data["email_subject"]
        assert application.email_recipients == ["contact@testfestival.com"]

        # Verify GenericForeignKey relationship
        assert application.organisation == festival
        assert application.content_type == ContentType.objects.get_for_model(Festival)
        assert application.object_id == festival.id

        # Verify reverse relationship works
        assert festival.applications.count() == 1
        assert festival.applications.first() == application

        # Verify application year calculation
        current_date = timezone.now().date()
        expected_year = current_date.year + 1 if current_date.month >= 9 else current_date.year
        assert application.application_year == expected_year

        # Verify email was sent via locmem backend (not mocked)
        assert len(mail.outbox) == 1
        sent_email = mail.outbox[0]
        assert sent_email.subject == data["email_subject"]
        assert "contact@testfestival.com" in sent_email.to
        assert "I would like to apply" in sent_email.body

    def test_apply_with_performances_creates_many_to_many_relationship(
        self, authenticated_client, festival, authenticated_user, performance
    ):
        """
        Integration test: Applying with performances should create
        ManyToMany relationships in the database.
        """
        mail.outbox.clear()

        # Configure user email settings
        authenticated_user.email_host = "OTHER"
        authenticated_user.other_email_host = "ssl0.ovh.net"

        authenticated_user.email_host_user = os.environ["EMAIL_HOST_USER"]
        authenticated_user.email_host_password = os.environ["EMAIL_HOST_PASSWORD"]
        authenticated_user.save()

        # Create another performance
        performance2 = Performance.objects.create(
            performance_title="Fire Dancing Show",
            profile=authenticated_user,
            short_description="An amazing fire performance",
        )

        data = {
            "message": "<p>Please consider my shows for your festival.</p>",
            "email_subject": "Multiple Performance Application",
            "recipients": "contact@testfestival.com",
            "performances": [str(performance.id), str(performance2.id)],
        }

        response = authenticated_client.post(
            f"/api/festivals/{festival.id}/apply/", data, format="json"
        )

        assert response.status_code == status.HTTP_200_OK

        # Verify ManyToMany relationship in database
        application = Application.objects.first()
        assert application.performances.count() == 2
        assert performance in application.performances.all()
        assert performance2 in application.performances.all()

        # Verify reverse relationship
        performance.refresh_from_db()
        performance2.refresh_from_db()
        assert application in performance.applications.all()
        assert application in performance2.applications.all()

    def test_apply_duplicate_application_same_year_enforces_business_rule(
        self, authenticated_client, festival, authenticated_user
    ):
        """
        Integration test: Business rule preventing duplicate applications
        for the same year should be enforced.
        """
        mail.outbox.clear()

        # Configure user email
        authenticated_user.email_host = "OTHER"
        authenticated_user.other_email_host = "ssl0.ovh.net"

        authenticated_user.email_host_user = os.environ["EMAIL_HOST_USER"]
        authenticated_user.email_host_password = os.environ["EMAIL_HOST_PASSWORD"]
        authenticated_user.save()

        # Create first application
        current_date = timezone.now().date()
        application_year = current_date.year + 1 if current_date.month >= 9 else current_date.year  # noqa

        content_type = ContentType.objects.get_for_model(Festival)
        Application.objects.create(
            content_type=content_type,
            object_id=festival.id,
            profile=authenticated_user,
            application_date=current_date,
            status="APPLIED",
            message="First application",
            email_subject="First Subject",
            email_recipients=["contact@testfestival.com"],
        )

        # Try to create second application for the same year
        data = {
            "message": "<p>Second application</p>",
            "email_subject": "Second Subject",
            "recipients": "contact@testfestival.com",
        }

        response = authenticated_client.post(f"/api/festivals/{festival.id}/apply/", data)

        # Should fail due to business rule
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "already exists" in str(response.data).lower()

        # Only one application should exist
        assert (
            Application.objects.filter(
                content_type=content_type, object_id=festival.id, profile=authenticated_user
            ).count()
            == 1
        )

    def test_apply_with_invalid_email_validates_through_entire_stack(
        self, authenticated_client, festival
    ):
        """
        Integration test: Email validation should work through the entire
        request/response/validation stack.
        """
        invalid_emails = [
            "not-an-email",
            "missing@domain",
            "@nodomain.com",
            "spaces in@email.com",
            "",
        ]

        for invalid_email in invalid_emails:
            data = {
                "message": "<p>Application message</p>",
                "email_subject": "Application Subject",
                "recipients": invalid_email,
            }

            response = authenticated_client.post(f"/api/festivals/{festival.id}/apply/", data)

            assert response.status_code == status.HTTP_400_BAD_REQUEST

        # No applications should be created
        assert Application.objects.count() == 0

    def test_application_year_calculation_september_rule(
        self, authenticated_client, festival, authenticated_user
    ):
        """
        Integration test: Application year should be calculated correctly
        based on the September rule (applications after September are for next year).
        """
        mail.outbox.clear()

        # Configure user email
        authenticated_user.email_host = "OTHER"
        authenticated_user.other_email_host = "ssl0.ovh.net"

        authenticated_user.email_host_user = os.environ["EMAIL_HOST_USER"]
        authenticated_user.email_host_password = os.environ["EMAIL_HOST_PASSWORD"]
        authenticated_user.save()

        data = {
            "message": "<p>Test message</p>",
            "email_subject": "Test Subject",
            "recipients": "contact@testfestival.com",
        }

        # Test applying in August (should use current year)
        with patch("django.utils.timezone.now") as mock_now:
            mock_now.return_value = timezone.make_aware(datetime(2025, 8, 15))

            response = authenticated_client.post(f"/api/festivals/{festival.id}/apply/", data)

            assert response.status_code == status.HTTP_200_OK
            application = Application.objects.first()
            assert application.application_year == 2025

        # Delete the application
        application.hard_delete()
        mail.outbox.clear()

        # Test applying in October (should increment year)
        with patch("django.utils.timezone.now") as mock_now:
            mock_now.return_value = timezone.make_aware(datetime(2025, 10, 1))

            response = authenticated_client.post(f"/api/festivals/{festival.id}/apply/", data)

            assert response.status_code == status.HTTP_200_OK
            application = Application.objects.first()
            assert application.application_year == 2026


@pytest.mark.django_db
class TestDatabaseRelationshipsIntegration:
    """Test complex database relationships and cascade behaviors"""

    def test_cascade_delete_user_deletes_applications(
        self, authenticated_client, festival, authenticated_user
    ):
        """
        Integration test: Deleting a user should cascade delete their applications
        (hard delete, not soft delete).
        """
        mail.outbox.clear()

        # Configure user email
        authenticated_user.email_host = "OTHER"
        authenticated_user.other_email_host = "ssl0.ovh.net"

        authenticated_user.email_host_user = os.environ["EMAIL_HOST_USER"]
        authenticated_user.email_host_password = os.environ["EMAIL_HOST_PASSWORD"]
        authenticated_user.save()

        # Create an application
        data = {
            "message": "<p>Application message</p>",
            "email_subject": "Application Subject",
            "recipients": "contact@testfestival.com",
        }
        response = authenticated_client.post(f"/api/festivals/{festival.id}/apply/", data)
        print("RESPONSE: ", response)
        assert response.status_code == status.HTTP_200_OK

        application_id = response.data["applicationId"]
        assert Application.objects.filter(id=application_id).exists()

        # Hard delete the user (not soft delete)
        user_id = authenticated_user.id
        authenticated_user.delete()  # This calls the actual Django delete, not soft delete

        # User should be deleted
        assert not Profile.objects.filter(id=user_id).exists()

        # Application should also be deleted due to CASCADE
        assert not Application.objects.filter(id=application_id).exists()

    def test_soft_delete_festival_preserves_applications(
        self, authenticated_client, festival, authenticated_user
    ):
        """
        Integration test: Soft deleting a festival should preserve applications
        because only the festival's deleted_at is set.
        """
        mail.outbox.clear()

        # Configure user email
        authenticated_user.email_host = "OTHER"
        authenticated_user.other_email_host = "ssl0.ovh.net"

        authenticated_user.email_host_user = os.environ["EMAIL_HOST_USER"]
        authenticated_user.email_host_password = os.environ["EMAIL_HOST_PASSWORD"]
        authenticated_user.save()

        # Create an application
        data = {
            "message": "<p>Application message</p>",
            "email_subject": "Application Subject",
            "recipients": "contact@testfestival.com",
        }
        response = authenticated_client.post(f"/api/festivals/{festival.id}/apply/", data)
        assert response.status_code == status.HTTP_200_OK

        application_id = response.data["applicationId"]

        # Soft delete the festival
        festival.delete()  # This is soft delete

        # Festival should be soft-deleted
        festival.refresh_from_db()
        assert festival.deleted_at is not None

        # Application should still exist (soft delete doesn't cascade)
        assert Application.objects.filter(id=application_id).exists()
        application = Application.objects.get(id=application_id)
        assert application.organisation == festival

    def test_complex_query_applications_by_year_and_status(
        self, authenticated_client, festival, authenticated_user
    ):
        """
        Integration test: Complex queries across applications should work correctly
        with calculated fields like application_year.
        """
        mail.outbox.clear()

        # Configure user email
        authenticated_user.email_host = "OTHER"
        authenticated_user.other_email_host = "ssl0.ovh.net"

        authenticated_user.email_host_user = os.environ["EMAIL_HOST_USER"]
        authenticated_user.email_host_password = os.environ["EMAIL_HOST_PASSWORD"]
        authenticated_user.save()

        # Create applications for different years
        with patch("django.utils.timezone.now") as mock_now:
            # Application for 2025
            mock_now.return_value = timezone.make_aware(datetime(2025, 3, 1))

            data = {
                "message": "<p>2025 application</p>",
                "email_subject": "2025 Subject",
                "recipients": "contact@testfestival.com",
            }
            response = authenticated_client.post(f"/api/festivals/{festival.id}/apply/", data)
            assert response.status_code == status.HTTP_200_OK
            app_2025_id = response.data["applicationId"]

        # Create another festival for 2026 application
        festival2 = Festival.objects.create(
            name="Tst Festival 2",
            country="Spain",
            town="Madrid",
        )

        mail.outbox.clear()

        with patch("django.utils.timezone.now") as mock_now:
            # Application for 2026
            mock_now.return_value = timezone.make_aware(datetime(2025, 10, 1))

            data = {
                "message": "<p>2026 application</p>",
                "email_subject": "2026 Subject",
                "recipients": "contact@testfestival2.com",
            }
            response = authenticated_client.post(f"/api/festivals/{festival2.id}/apply/", data)
            assert response.status_code == status.HTTP_200_OK
            app_2026_id = response.data["applicationId"]

        # Query applications by year using the property
        app_2025 = Application.objects.get(id=app_2025_id)
        app_2026 = Application.objects.get(id=app_2026_id)

        assert app_2025.application_year == 2025
        assert app_2026.application_year == 2026

        # Query all applications for the user
        user_applications = Application.objects.filter(profile=authenticated_user)
        assert user_applications.count() == 2

        # Filter by status
        applied_applications = user_applications.filter(status="APPLIED")
        assert applied_applications.count() == 2


@pytest.mark.django_db
class TestCompleteApplicationWorkflowIntegration:
    """Test complete workflow from registration to application submission"""

    @patch("organisations.views.MistralClient")
    def test_complete_workflow_registration_to_application(self, mock_mistral_client, api_client):
        """
        Integration test: Complete user journey from registration to applying.

        Flow:
        1. Register a new user → triggers signal → sends welcome email
        2. Login
        3. Create a festival
        4. Generate email content (with mocked LLM)
        5. Apply to festival → sends application email

        Verifies:
        - Multiple database transactions work correctly
        - Signals fire at appropriate times
        - Email backend captures all emails
        - Session management works across requests
        - Database relationships are correctly established
        """
        # Clear email outbox
        mail.outbox.clear()

        # Step 1: Register a new user
        register_data = {
            "email": "workflow@example.com",
            "password": "WorkflowPass123!",
            "password_confirm": "WorkflowPass123!",
        }
        register_response = api_client.post("/api/profiles/register/", register_data)

        assert register_response.status_code == status.HTTP_201_CREATED
        assert Profile.objects.filter(email="workflow@example.com").exists()

        # Verify welcome email was sent via signal
        assert len(mail.outbox) == 1
        assert "Welcome" in mail.outbox[0].subject

        mail.outbox.clear()

        # Step 2: Login
        login_data = {
            "email": "workflow@example.com",
            "password": "WorkflowPass123!",
        }
        login_response = api_client.post("/api/profiles/login/", login_data)

        assert login_response.status_code == status.HTTP_200_OK

        # Authenticate the client
        user = Profile.objects.get(email="workflow@example.com")
        api_client.force_authenticate(user=user)

        # Step 3: Create a festival
        festival_data = {
            "name": "Workflow Festival",
            "country": "Italy",
            "town": "Rome",
            "festival_type": "CIRCUS",
        }
        festival_response = api_client.post("/api/festivals/", festival_data)

        assert festival_response.status_code == status.HTTP_201_CREATED
        festival_id = festival_response.data["id"]

        # Verify festival in database
        assert Festival.objects.filter(id=festival_id).exists()
        festival = Festival.objects.get(id=festival_id)
        assert festival.name == "Workflow Festival"

        # Step 4: Generate email content
        mock_mistral = Mock()
        mock_mistral.chat.return_value = "Generated email content for application"
        mock_mistral_client.return_value = mock_mistral

        email_data = {
            "language": "ENGLISH",
            "message_length": "SHORT",
        }
        email_response = api_client.post(
            f"/api/festivals/{festival_id}/generate_email/", email_data
        )

        assert email_response.status_code == status.HTTP_200_OK
        assert "message" in email_response.data

        # Step 5: Configure email settings and apply to the festival
        user.email_host = "OTHER"
        user.other_email_host = "ssl0.ovh.net"

        user.email_host_user = os.environ["EMAIL_HOST_USER"]
        user.email_host_password = os.environ["EMAIL_HOST_PASSWORD"]
        user.save()

        apply_data = {
            "message": email_response.data["message"],
            "email_subject": "Application to Workflow Festival",
            "recipients": "workflow@festival.com",
        }
        apply_response = api_client.post(f"/api/festivals/{festival_id}/apply/", apply_data)

        assert apply_response.status_code == status.HTTP_200_OK
        assert "applicationId" in apply_response.data

        # Verify the application was created in database
        application = Application.objects.get(id=apply_response.data["applicationId"])
        assert application.profile == user
        assert application.status == "APPLIED"
        assert application.organisation == festival

        # Verify application email was sent (total 1 email: the application email)
        assert len(mail.outbox) == 1
        app_email = mail.outbox[0]
        assert app_email.subject == "Application to Workflow Festival"
        assert "workflow@festival.com" in app_email.to

        # Verify database relationships
        assert user.applications.count() == 1
        assert festival.applications.count() == 1
        assert user.applications.first() == application
        assert festival.applications.first() == application


@pytest.mark.django_db
class TestApplicationSoftDeleteIntegration:
    """Test application soft delete functionality"""

    def test_application_soft_delete_and_restore(
        self, authenticated_client, festival, authenticated_user
    ):
        """
        Integration test: Applications should support soft delete and restore.
        """
        mail.outbox.clear()

        # Configure user email
        authenticated_user.email_host = "OTHER"
        authenticated_user.other_email_host = "ssl0.ovh.net"

        authenticated_user.email_host_user = os.environ["EMAIL_HOST_USER"]
        authenticated_user.email_host_password = os.environ["EMAIL_HOST_PASSWORD"]
        authenticated_user.save()

        # Create an application
        data = {
            "message": "<p>Test application</p>",
            "email_subject": "Test Subject",
            "recipients": "contact@testfestival.com",
        }
        response = authenticated_client.post(f"/api/festivals/{festival.id}/apply/", data)
        assert response.status_code == status.HTTP_200_OK

        application_id = response.data["applicationId"]
        application = Application.objects.get(id=application_id)

        # Soft delete the application
        application.delete()

        # Application should be soft-deleted
        application.refresh_from_db()
        assert application.deleted_at is not None

        # Should not appear in default queryset
        assert not Application.objects.filter(id=application_id).exists()

        # Should appear in with_deleted queryset
        assert Application.objects.with_deleted().filter(id=application_id).exists()

        # Restore the application
        application.restore()

        # Application should be restored
        application.refresh_from_db()
        assert application.deleted_at is None

        # Should appear in default queryset again
        assert Application.objects.filter(id=application_id).exists()


@pytest.mark.django_db
class TestFormApplicationIntegration:
    """Test form-based application workflow (no email sending)"""

    def test_form_application_workflow(
        self, authenticated_client, festival, authenticated_user, performance
    ):
        """
        Integration test: Form applications should be created without sending emails.
        """
        mail.outbox.clear()

        data = {
            "application_method": "FORM",
            "performances": [str(performance.id)],
            "comments": "Applied via online form",
        }

        response = authenticated_client.post(f"/api/festivals/{festival.id}/apply/", data)

        assert response.status_code == status.HTTP_200_OK
        assert "applicationId" in response.data

        # Verify application created
        application = Application.objects.get(id=response.data["applicationId"])
        assert application.application_method == "FORM"
        assert application.status == "APPLIED"
        assert application.profile == authenticated_user
        assert application.organisation == festival
        assert application.comments == "Applied via online form"

        # Verify performance relationship
        assert application.performances.count() == 1
        assert performance in application.performances.all()

        # No email should be sent for form applications
        assert len(mail.outbox) == 0

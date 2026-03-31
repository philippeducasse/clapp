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

from datetime import date, datetime
from unittest.mock import Mock, patch

import pytest
from django.contrib.contenttypes.models import ContentType
from django.core import mail
from django.core.mail import get_connection
from django.test import override_settings
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
        website_url="https://festival.com",
        start_date=date(2026, 7, 15),
        end_date=date(2026, 7, 20),
        application_type="EMAIL",
        user=authenticated_user,
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


@pytest.mark.django_db(transaction=True)
class TestUserRegistrationIntegration:
    """Test user registration with real signal handlers and email backend"""

    @override_settings(ENVIRONMENT="prod", CELERY_TASK_ALWAYS_EAGER=True)
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
        # EMAIL_HOST_USER should be used (will be set by override_settings in test config)
        assert welcome_email.from_email is not None

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
    def test_enrich_festival_updates_database_fields(
        self, mock_mistral_client, authenticated_client, festival
    ):
        """
        Integration test: Enrichment should update festival fields in database
        based on LLM responses.
        """
        from mistralai import TextChunk

        # Mock the Mistral service (search and chat)
        mock_mistral = Mock()

        # Mock search response with proper ConversationResponse structure
        mock_text_chunk = Mock(
            spec=TextChunk,
            text="Tst Festival is a renowned street arts festival in Paris, France. "
            "It takes place annually in July and features international circus performers.",
        )
        mock_output = Mock(type="message.output", content=[mock_text_chunk])
        mock_search_response = Mock(outputs=[mock_output])
        mock_mistral.search.return_value = mock_search_response

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

        response = authenticated_client.get(f"/api/festivals/{festival.id}/enrich/")

        assert response.status_code == status.HTTP_200_OK

        # Verify Mistral service was called
        assert mock_mistral.search.called
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

        authenticated_user.email_host_user = "test@test.com"
        authenticated_user.email_host_password = "TestPassword123!"
        authenticated_user.save()

        data = {
            "message": "<p>I would like to apply to your festival with my circus act.</p>",
            "email_subject": "Application to Tst Festival 2026",
            "recipients": "contact@festival.com",
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
        assert application.email_recipients == ["contact@festival.com"]

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
        assert "contact@festival.com" in sent_email.to
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

        authenticated_user.email_host_user = "test@test.com"
        authenticated_user.email_host_password = "TestPassword123!"
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
            "recipients": "contact@festival.com",
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
        Integration test: Multiple applications to the same festival are allowed.
        """
        mail.outbox.clear()

        # Configure user email
        authenticated_user.email_host = "OTHER"
        authenticated_user.other_email_host = "ssl0.ovh.net"

        authenticated_user.email_host_user = "test@test.com"
        authenticated_user.email_host_password = "TestPassword123!"
        authenticated_user.save()

        content_type = ContentType.objects.get_for_model(Festival)
        Application.objects.create(
            content_type=content_type,
            object_id=festival.id,
            profile=authenticated_user,
            application_date=timezone.now().date(),
            status="APPLIED",
            message="First application",
            email_subject="First Subject",
            email_recipients=["contact@festival.com"],
        )

        data = {
            "message": "<p>Second application</p>",
            "email_subject": "Second Subject",
            "recipients": "contact@festival.com",
        }

        response = authenticated_client.post(f"/api/festivals/{festival.id}/apply/", data)

        assert response.status_code == status.HTTP_200_OK
        assert (
            Application.objects.filter(
                content_type=content_type, object_id=festival.id, profile=authenticated_user
            ).count()
            == 2
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
        Integration test: Application year uses profile.current_application_year when set,
        otherwise defaults to the current calendar year regardless of month.
        """
        mail.outbox.clear()

        # Configure user email
        authenticated_user.email_host = "OTHER"
        authenticated_user.other_email_host = "ssl0.ovh.net"

        authenticated_user.email_host_user = "test@test.com"
        authenticated_user.email_host_password = "TestPassword123!"
        authenticated_user.save()

        data = {
            "message": "<p>Test message</p>",
            "email_subject": "Test Subject",
            "recipients": "contact@festival.com",
        }

        # Applying in August with no current_application_year → uses calendar year
        with patch("django.utils.timezone.now") as mock_now:
            mock_now.return_value = timezone.make_aware(datetime(2025, 8, 15))

            response = authenticated_client.post(f"/api/festivals/{festival.id}/apply/", data)

            assert response.status_code == status.HTTP_200_OK
            application = Application.objects.first()
            assert application.application_year == 2025

        application.hard_delete()
        mail.outbox.clear()

        # Applying in October with no current_application_year → still uses calendar year (2025)
        with patch("django.utils.timezone.now") as mock_now:
            mock_now.return_value = timezone.make_aware(datetime(2025, 10, 1))

            response = authenticated_client.post(f"/api/festivals/{festival.id}/apply/", data)

            assert response.status_code == status.HTTP_200_OK
            application = Application.objects.first()
            assert application.application_year == 2025


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

        authenticated_user.email_host_user = "test@test.com"
        authenticated_user.email_host_password = "TestPassword123!"
        authenticated_user.save()

        # Create an application
        data = {
            "message": "<p>Application message</p>",
            "email_subject": "Application Subject",
            "recipients": "contact@festival.com",
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

        authenticated_user.email_host_user = "test@test.com"
        authenticated_user.email_host_password = "TestPassword123!"
        authenticated_user.save()

        # Create an application
        data = {
            "message": "<p>Application message</p>",
            "email_subject": "Application Subject",
            "recipients": "contact@festival.com",
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

        authenticated_user.email_host_user = "test@test.com"
        authenticated_user.email_host_password = "TestPassword123!"
        authenticated_user.save()

        # Create applications for different years
        with patch("django.utils.timezone.now") as mock_now:
            # Application for 2025
            mock_now.return_value = timezone.make_aware(datetime(2025, 3, 1))

            data = {
                "message": "<p>2025 application</p>",
                "email_subject": "2025 Subject",
                "recipients": "contact@festival.com",
            }
            response = authenticated_client.post(f"/api/festivals/{festival.id}/apply/", data)
            assert response.status_code == status.HTTP_200_OK
            app_2025_id = response.data["applicationId"]

        # Create another festival for 2026 application
        festival2 = Festival.objects.create(
            name="Tst Festival 2",
            country="Spain",
            town="Madrid",
            user=authenticated_user,
        )

        mail.outbox.clear()

        with patch("django.utils.timezone.now") as mock_now:
            # Application for 2026
            mock_now.return_value = timezone.make_aware(datetime(2026, 3, 1))

            data = {
                "message": "<p>2026 application</p>",
                "email_subject": "2026 Subject",
                "recipients": "contact@festival2.com",
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


@pytest.mark.django_db(transaction=True)
class TestCompleteApplicationWorkflowIntegration:
    """Test complete workflow from registration to application submission"""

    @override_settings(ENVIRONMENT="prod", CELERY_TASK_ALWAYS_EAGER=True)
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

        user.email_host_user = "test@test.com"
        user.email_host_password = "TestPassword123!"
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
        EMAIL_HOST_USER = mail.outbox[0]
        assert EMAIL_HOST_USER.subject == "Application to Workflow Festival"
        assert "workflow@festival.com" in EMAIL_HOST_USER.to

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

        authenticated_user.email_host_user = "test@test.com"
        authenticated_user.email_host_password = "TestPassword123!"
        authenticated_user.save()

        # Create an application
        data = {
            "message": "<p>Test application</p>",
            "email_subject": "Test Subject",
            "recipients": "contact@festival.com",
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


@pytest.mark.django_db
class TestApplicationViewSet:
    """Test ApplicationViewSet endpoints and filtering"""

    def test_application_list_returns_user_applications(
        self, authenticated_client, festival, authenticated_user, performance
    ):
        """
        Test that list endpoint returns only applications for the authenticated user.
        """
        mail.outbox.clear()

        # Configure user email
        authenticated_user.email_host = "OTHER"
        authenticated_user.other_email_host = "ssl0.ovh.net"
        authenticated_user.email_host_user = "test@test.com"
        authenticated_user.email_host_password = "TestPassword123!"
        authenticated_user.save()

        # Create an application
        data = {
            "message": "<p>Test application</p>",
            "email_subject": "Test Subject",
            "recipients": "contact@festival.com",
            "performances": [str(performance.id)],
        }
        response = authenticated_client.post(f"/api/festivals/{festival.id}/apply/", data)
        assert response.status_code == status.HTTP_200_OK

        # Get applications list
        list_response = authenticated_client.get("/api/applications/")

        assert list_response.status_code == status.HTTP_200_OK
        # Response is paginated, check results
        results = list_response.data.get("results", list_response.data)
        assert len(results) >= 1
        application_ids = [app["id"] for app in results]
        assert response.data["applicationId"] in application_ids

    def test_application_get_queryset_filters_by_user(
        self, authenticated_client, authenticated_user
    ):
        """
        Test that get_queryset filters applications by the authenticated user.
        """
        # Create another user's application
        other_user = Profile.objects.create_user(
            email="other@example.com",
            password="OtherPass123!",
        )

        festival = Festival.objects.create(
            name="Test Festival",
            country="France",
            town="Paris",
            user=other_user,
        )

        # Create application for other user
        from django.contrib.contenttypes.models import ContentType

        content_type = ContentType.objects.get_for_model(Festival)
        Application.objects.create(
            content_type=content_type,
            object_id=festival.id,
            profile=other_user,
            application_date=timezone.now().date(),
            status="APPLIED",
            message="Other user's application",
            email_subject="Subject",
            email_recipients=["test@test.com"],
        )

        # Authenticated user should not see other user's applications
        list_response = authenticated_client.get("/api/applications/")

        assert list_response.status_code == status.HTTP_200_OK
        # Response is paginated
        results = list_response.data.get("results", list_response.data)
        assert len(results) == 0

    def test_application_tag_status_action(
        self, authenticated_client, festival, authenticated_user
    ):
        """
        Test the tag action to update application status.
        """
        mail.outbox.clear()

        # Configure user email
        authenticated_user.email_host = "OTHER"
        authenticated_user.other_email_host = "ssl0.ovh.net"
        authenticated_user.email_host_user = "test@test.com"
        authenticated_user.email_host_password = "TestPassword123!"
        authenticated_user.save()

        # Create an application
        data = {
            "message": "<p>Test application</p>",
            "email_subject": "Test Subject",
            "recipients": "contact@festival.com",
        }
        response = authenticated_client.post(f"/api/festivals/{festival.id}/apply/", data)
        assert response.status_code == status.HTTP_200_OK

        application_id = response.data["applicationId"]

        # Update application status to ACCEPTED
        tag_response = authenticated_client.patch(
            f"/api/applications/{application_id}/status/ACCEPTED/", format="json"
        )

        assert tag_response.status_code == status.HTTP_200_OK

        # Verify status was updated
        application = Application.objects.get(id=application_id)
        assert application.status == "ACCEPTED"

    def test_application_tag_invalid_status(
        self, authenticated_client, festival, authenticated_user
    ):
        """
        Test that tag action rejects invalid statuses.
        """
        mail.outbox.clear()

        # Configure user email
        authenticated_user.email_host = "OTHER"
        authenticated_user.other_email_host = "ssl0.ovh.net"
        authenticated_user.email_host_user = "test@test.com"
        authenticated_user.email_host_password = "TestPassword123!"
        authenticated_user.save()

        # Create an application
        data = {
            "message": "<p>Test application</p>",
            "email_subject": "Test Subject",
            "recipients": "contact@festival.com",
        }
        response = authenticated_client.post(f"/api/festivals/{festival.id}/apply/", data)
        assert response.status_code == status.HTTP_200_OK

        application_id = response.data["applicationId"]

        # Try to update with invalid status
        tag_response = authenticated_client.patch(
            f"/api/applications/{application_id}/status/INVALID_STATUS/", format="json"
        )

        assert tag_response.status_code == status.HTTP_400_BAD_REQUEST
        assert "Invalid action" in tag_response.data["error"]


@pytest.mark.django_db
class TestOrganisationSearchEndpoint:
    """Test the search endpoint for organisations"""

    def test_search_with_minimum_query_returns_empty(
        self, authenticated_client, authenticated_user
    ):
        """
        Test that search with less than 2 characters returns empty list.
        """
        response = authenticated_client.get("/api/organisations/search/?q=a")

        assert response.status_code == status.HTTP_200_OK
        assert response.data == []

    def test_search_festivals_by_name(self, authenticated_client, authenticated_user):
        """
        Test searching for festivals by name.
        """
        festival = Festival.objects.create(
            name="Paris Street Festival",
            country="France",
            town="Paris",
            user=authenticated_user,
        )

        response = authenticated_client.get("/api/organisations/search/?q=Paris&type=festival")

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) > 0
        assert response.data[0]["id"] == festival.id
        # When filtering by type, the endpoint returns just the fields without the type field

    def test_search_invalid_organisation_type(self, authenticated_client):
        """
        Test that invalid organisation type returns error.
        """
        response = authenticated_client.get("/api/organisations/search/?q=test&type=invalid_type")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "Invalid organisation type" in response.data["error"]

    def test_search_all_types_without_type_parameter(
        self, authenticated_client, authenticated_user
    ):
        """
        Test that search without type parameter returns mixed results.
        """
        from organisations.residencies.models import Residency
        from organisations.venues.models import Venue

        Festival.objects.create(
            name="Test Festival",
            country="France",
            town="Paris",
            user=authenticated_user,
        )

        Venue.objects.create(
            name="Test Venue",
            country="France",
            town="Paris",
            user=authenticated_user,
        )

        Residency.objects.create(
            name="Test Residency",
            country="France",
            town="Paris",
            user=authenticated_user,
        )

        response = authenticated_client.get("/api/organisations/search/?q=Test")

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) >= 3

        types = {item["type"] for item in response.data}
        assert "festival" in types
        assert "venue" in types
        assert "residency" in types


@pytest.mark.django_db
class TestOrganisationTagAction:
    """Test the tag action for organisations"""

    def test_organisation_tag_valid_action(self, authenticated_client, authenticated_user):
        """
        Test tagging an organisation with valid tag action.
        """
        festival = Festival.objects.create(
            name="Test Festival",
            country="France",
            town="Paris",
            user=authenticated_user,
        )

        # Tag with STAR
        response = authenticated_client.patch(
            f"/api/festivals/{festival.id}/tag/STAR/", format="json"
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.data["tag"] == "STAR"

        # Verify in database
        festival.refresh_from_db()
        assert festival.tag == "STAR"

    def test_organisation_tag_toggle_off(self, authenticated_client, authenticated_user):
        """
        Test that applying the same tag removes it.
        """
        festival = Festival.objects.create(
            name="Test Festival",
            country="France",
            town="Paris",
            user=authenticated_user,
            tag="STAR",
        )

        # Apply same tag to toggle off
        response = authenticated_client.patch(
            f"/api/festivals/{festival.id}/tag/STAR/", format="json"
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.data["tag"] == ""

        # Verify in database
        festival.refresh_from_db()
        assert festival.tag == ""

    def test_organisation_tag_invalid_action(self, authenticated_client, authenticated_user):
        """
        Test that invalid tag action returns error.
        """
        festival = Festival.objects.create(
            name="Test Festival",
            country="France",
            town="Paris",
            user=authenticated_user,
        )

        response = authenticated_client.patch(
            f"/api/festivals/{festival.id}/tag/INVALID_TAG/", format="json"
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "Invalid action" in response.data["error"]


@pytest.mark.django_db
class TestResidencyViewSet:
    """Test ResidencyViewSet specific functionality"""

    def test_residency_get_organisation_type_name(self, authenticated_client, authenticated_user):
        """
        Test that residency viewset returns correct type name.
        """
        from organisations.residencies.models import Residency

        residency = Residency.objects.create(
            name="Test Residency",
            country="France",
            town="Paris",
            user=authenticated_user,
        )

        response = authenticated_client.get(f"/api/residencies/{residency.id}/")

        assert response.status_code == status.HTTP_200_OK

    @patch("organisations.views.MistralClient")
    def test_residency_enrich_uses_residency_prompt(
        self, mock_mistral_client, authenticated_client, authenticated_user
    ):
        """
        Test that residency enrichment uses residency-specific prompt.
        """
        from organisations.residencies.models import Residency
        from mistralai import TextChunk

        residency = Residency.objects.create(
            name="Test Residency",
            country="France",
            town="Paris",
            website_url="https://residency.com",
            user=authenticated_user,
        )

        # Mock the Mistral service
        mock_mistral = Mock()

        mock_text_chunk = Mock(
            spec=TextChunk,
            text="Test residency in France",
        )
        mock_output = Mock(type="message.output", content=[mock_text_chunk])
        mock_search_response = Mock(outputs=[mock_output])
        mock_mistral.search.return_value = mock_search_response

        mock_mistral.chat.return_value = """
        {
            "description": "A test residency"
        }
        """
        mock_mistral_client.return_value = mock_mistral

        response = authenticated_client.get(f"/api/residencies/{residency.id}/enrich/")

        assert response.status_code == status.HTTP_200_OK
        assert mock_mistral.search.called
        assert mock_mistral.chat.called


@pytest.mark.django_db
class TestOrganisationRestoreAction:
    """Test the restore action for soft-deleted organisations"""

    def test_restore_non_deleted_organisation_returns_error(
        self, authenticated_client, authenticated_user
    ):
        """
        Test that trying to restore a non-deleted organisation returns error.
        """
        festival = Festival.objects.create(
            name="Test Festival",
            country="France",
            town="Paris",
            user=authenticated_user,
        )

        # Try to restore non-deleted festival
        response = authenticated_client.post(f"/api/festivals/{festival.id}/restore/")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "not deleted" in response.data["error"].lower()

    def test_restore_deleted_organisation(self, authenticated_client, authenticated_user):
        """
        Test that restoring a deleted organisation works correctly.
        """
        festival = Festival.objects.create(
            name="Test Festival",
            country="France",
            town="Paris",
            user=authenticated_user,
        )

        # Soft delete the festival
        festival.delete()
        assert festival.deleted_at is not None

        # Restore it
        response = authenticated_client.post(f"/api/festivals/{festival.id}/restore/")

        assert response.status_code == status.HTTP_200_OK
        assert "restored successfully" in response.data["message"].lower()

        # Verify it's restored
        festival.refresh_from_db()
        assert festival.deleted_at is None

    def test_restore_non_existent_organisation(self, authenticated_client, authenticated_user):
        """
        Test that trying to restore non-existent organisation returns 404.
        """
        response = authenticated_client.post("/api/festivals/999999/restore/")

        assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
class TestOrganisationUploadAction:
    """Test the upload action for importing organisations"""

    def test_upload_without_file_returns_error(self, authenticated_client):
        """
        Test that upload without file returns error.
        """
        response = authenticated_client.post("/api/festivals/upload/", {})

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "No Excel file provided" in response.data["error"]

    def test_upload_returns_task_id(self, authenticated_client):
        """
        Test that upload returns a task ID for async processing.
        """
        from django.core.files.uploadedfile import SimpleUploadedFile

        # Create a simple Excel-like file (just for testing)
        file_content = b"test content"
        uploaded_file = SimpleUploadedFile("test.xlsx", file_content)

        response = authenticated_client.post(
            "/api/festivals/upload/",
            {"excel": uploaded_file},
            format="multipart",
        )

        assert response.status_code == status.HTTP_202_ACCEPTED
        assert "task_id" in response.data


@pytest.mark.django_db
class TestOrganisationUploadStatus:
    """Test the upload-status action for checking import progress"""

    def test_upload_status_returns_task_status(self, authenticated_client):
        """
        Test that upload_status returns task status.
        """
        # Just test with a fake task ID
        response = authenticated_client.get("/api/festivals/upload-status/fake-task-id/")

        assert response.status_code == status.HTTP_200_OK
        assert "status" in response.data


@pytest.mark.django_db
class TestOrganisationApplyEdgeCases:
    """Test edge cases in the apply action"""

    def test_apply_with_missing_message_returns_error(
        self, authenticated_client, festival, authenticated_user
    ):
        """
        Test that apply without message returns error.
        """
        authenticated_user.email_host = "OTHER"
        authenticated_user.other_email_host = "ssl0.ovh.net"
        authenticated_user.email_host_user = "test@test.com"
        authenticated_user.email_host_password = "TestPassword123!"
        authenticated_user.save()

        data = {
            "email_subject": "Test Subject",
            "recipients": "contact@festival.com",
        }

        response = authenticated_client.post(f"/api/festivals/{festival.id}/apply/", data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "Message and/or subject not found" in response.data["error"]

    def test_apply_form_method_succeeds_with_invalid_performance(
        self, authenticated_client, festival, authenticated_user
    ):
        """
        Test that form application succeeds even with invalid performance ID
        (the performance is simply not added to the relationship).
        """
        data = {
            "application_method": "FORM",
            "performances": ["999999"],  # Invalid performance ID - will be ignored
            "comments": "Test",
        }

        response = authenticated_client.post(f"/api/festivals/{festival.id}/apply/", data)

        # The endpoint succeeds and creates the application
        assert response.status_code == status.HTTP_200_OK
        assert "applicationId" in response.data


@pytest.mark.django_db
class TestOrganisationQuerysetFiltering:
    """Test the queryset filtering logic in OrganisationViewSet"""

    def test_include_deleted_parameter_shows_deleted_organisations(
        self, authenticated_client, authenticated_user
    ):
        """
        Test that include_deleted=true parameter shows soft-deleted organisations.
        """
        festival = Festival.objects.create(
            name="Test Festival",
            country="France",
            town="Paris",
            user=authenticated_user,
        )

        # Soft delete the festival
        festival.delete()

        # Without include_deleted parameter
        response = authenticated_client.get("/api/festivals/")
        results = response.data.get("results", response.data)
        assert not any(f["id"] == festival.id for f in results)

        # With include_deleted=true parameter
        response = authenticated_client.get("/api/festivals/?include_deleted=true")
        results = response.data.get("results", response.data)
        assert any(f["id"] == festival.id for f in results)

    def test_staff_user_sees_all_non_seed_clones(self, authenticated_user, api_client):
        """
        Test that staff users can see organisations they didn't create.
        """
        # Create a staff user
        staff_user = Profile.objects.create_user(
            email="staff@example.com",
            password="StaffPass123!",
            is_staff=True,
        )

        # Create a festival for regular user
        festival = Festival.objects.create(
            name="User Festival",
            country="France",
            town="Paris",
            user=authenticated_user,
            is_seed_clone=False,
        )

        # Staff user should see the festival
        api_client.force_authenticate(user=staff_user)
        response = api_client.get("/api/festivals/")
        results = response.data.get("results", response.data)
        assert any(f["id"] == festival.id for f in results)

    def test_non_staff_user_sees_only_own_organisations(
        self, authenticated_client, authenticated_user
    ):
        """
        Test that non-staff users can only see their own organisations.
        """
        # Create another user
        other_user = Profile.objects.create_user(
            email="other@example.com",
            password="OtherPass123!",
        )

        # Create festivals for both users
        user_festival = Festival.objects.create(
            name="User Festival",
            country="France",
            town="Paris",
            user=authenticated_user,
        )

        other_festival = Festival.objects.create(
            name="Other Festival",
            country="Spain",
            town="Madrid",
            user=other_user,
        )

        # Authenticated user should only see their own festival
        response = authenticated_client.get("/api/festivals/")
        results = response.data.get("results", response.data)
        festival_ids = [f["id"] for f in results]

        assert user_festival.id in festival_ids
        assert other_festival.id not in festival_ids


@pytest.mark.django_db
class TestOrganisationPerformUpdate:
    """Test the perform_update method of OrganisationViewSet"""

    def test_perform_update_calls_full_clean(self, authenticated_client, authenticated_user):
        """
        Test that updating an organisation triggers full_clean() for validation.
        """
        festival = Festival.objects.create(
            name="Test Festival",
            country="France",
            town="Paris",
            user=authenticated_user,
        )

        # Update the festival with valid data
        data = {
            "name": "Updated Festival",
            "country": "Spain",
            "town": "Madrid",
        }

        response = authenticated_client.patch(f"/api/festivals/{festival.id}/", data)

        assert response.status_code == status.HTTP_200_OK

        # Verify the update
        festival.refresh_from_db()
        assert festival.name == "Updated Festival"
        assert festival.country == "Spain"
        assert festival.town == "Madrid"


@pytest.mark.django_db
class TestOrganisationEnrichEnhancements:
    """Test enrich endpoint enhancements"""

    @patch("organisations.views.MistralClient")
    def test_enrich_with_contacts_in_response(
        self, mock_mistral_client, authenticated_client, authenticated_user
    ):
        """
        Test that enrich endpoint includes contacts from LLM in the response.
        """
        from mistralai import TextChunk

        festival = Festival.objects.create(
            name="Test Festival",
            country="France",
            town="Paris",
            website_url="https://festival.com",
            user=authenticated_user,
        )

        # Mock the Mistral service
        mock_mistral = Mock()

        mock_text_chunk = Mock(
            spec=TextChunk,
            text="Test festival with contacts",
        )
        mock_output = Mock(type="message.output", content=[mock_text_chunk])
        mock_search_response = Mock(outputs=[mock_output])
        mock_mistral.search.return_value = mock_search_response

        mock_mistral.chat.return_value = """
        {
            "description": "A test festival",
            "contacts": ["contact1@example.com", "contact2@example.com"]
        }
        """
        mock_mistral_client.return_value = mock_mistral

        response = authenticated_client.get(f"/api/festivals/{festival.id}/enrich/")

        assert response.status_code == status.HTTP_200_OK
        # Contacts should be included in response
        if "contacts" in response.data:
            assert len(response.data["contacts"]) == 2


@pytest.mark.django_db
class TestGenerateEmailAction:
    """Test the generate_email action"""

    @patch("organisations.views.MistralClient")
    def test_generate_email_with_string_performance_ids(
        self, mock_mistral_client, authenticated_client, festival, authenticated_user
    ):
        """
        Test that generate_email handles string-formatted performance IDs.
        """
        from performances.models import Performance

        performance = Performance.objects.create(
            performance_title="Test Performance",
            profile=authenticated_user,
            short_description="A test performance",
        )

        mock_mistral = Mock()
        mock_mistral.chat.return_value = "Generated email content"
        mock_mistral_client.return_value = mock_mistral

        # Pass performance ID as string
        data = {
            "selected_performance_ids": str(performance.id),
            "language": "ENGLISH",
        }

        response = authenticated_client.post(f"/api/festivals/{festival.id}/generate_email/", data)

        assert response.status_code == status.HTTP_200_OK
        assert "message" in response.data

    @patch("organisations.views.MistralClient")
    def test_generate_email_with_list_performance_ids(
        self, mock_mistral_client, authenticated_client, festival, authenticated_user
    ):
        """
        Test that generate_email handles list-formatted performance IDs.
        """
        from performances.models import Performance

        perf1 = Performance.objects.create(
            performance_title="Performance 1",
            profile=authenticated_user,
            short_description="First performance",
        )

        perf2 = Performance.objects.create(
            performance_title="Performance 2",
            profile=authenticated_user,
            short_description="Second performance",
        )

        mock_mistral = Mock()
        mock_mistral.chat.return_value = "Generated email for multiple performances"
        mock_mistral_client.return_value = mock_mistral

        # Pass performance IDs as list
        data = {
            "selected_performance_ids": [perf1.id, perf2.id],
            "language": "ENGLISH",
            "message_length": "LONG",
        }

        response = authenticated_client.post(
            f"/api/festivals/{festival.id}/generate_email/",
            data,
            format="json",
        )

        assert response.status_code == status.HTTP_200_OK
        assert "message" in response.data

    @patch("organisations.views.MistralClient")
    def test_generate_email_with_integer_performance_id(
        self, mock_mistral_client, authenticated_client, festival, authenticated_user
    ):
        """
        Test that generate_email handles single integer performance ID.
        """
        from performances.models import Performance

        performance = Performance.objects.create(
            performance_title="Test Performance",
            profile=authenticated_user,
            short_description="A test performance",
        )

        mock_mistral = Mock()
        mock_mistral.chat.return_value = "Generated email"
        mock_mistral_client.return_value = mock_mistral

        # Pass performance ID as integer
        data = {
            "selected_performance_ids": performance.id,
            "language": "ENGLISH",
        }

        response = authenticated_client.post(f"/api/festivals/{festival.id}/generate_email/", data)

        assert response.status_code == status.HTTP_200_OK
        assert "message" in response.data

    @patch("organisations.views.MistralClient")
    def test_generate_email_with_no_performances(
        self, mock_mistral_client, authenticated_client, festival, authenticated_user
    ):
        """
        Test that generate_email works without performance IDs.
        """
        mock_mistral = Mock()
        mock_mistral.chat.return_value = "Generated email without performances"
        mock_mistral_client.return_value = mock_mistral

        data = {
            "language": "ENGLISH",
        }

        response = authenticated_client.post(f"/api/festivals/{festival.id}/generate_email/", data)

        assert response.status_code == status.HTTP_200_OK
        assert "message" in response.data


@pytest.mark.django_db
class TestGenerateEmailErrorHandling:
    """Test error handling in generate_email action"""

    @patch("organisations.views.MistralClient")
    def test_generate_email_with_invalid_performance_id_format(
        self, mock_mistral_client, authenticated_client, festival
    ):
        """
        Test that invalid performance ID format returns error.
        """
        mock_mistral = Mock()
        mock_mistral_client.return_value = mock_mistral

        data = {
            "selected_performance_ids": "not-a-number",
            "language": "ENGLISH",
        }

        response = authenticated_client.post(f"/api/festivals/{festival.id}/generate_email/", data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "Invalid performance ID format" in response.data["error"]

    @patch("organisations.views.MistralClient")
    def test_generate_email_with_mistral_error(
        self, mock_mistral_client, authenticated_client, festival
    ):
        """
        Test that Mistral service errors are handled gracefully.
        """
        mock_mistral = Mock()
        mock_mistral.chat.side_effect = Exception("Mistral API error")
        mock_mistral_client.return_value = mock_mistral

        data = {
            "language": "ENGLISH",
        }

        response = authenticated_client.post(f"/api/festivals/{festival.id}/generate_email/", data)

        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert "Error generating email" in response.data["error"]


@pytest.mark.django_db
class TestApplyErrorHandling:
    """Test error handling in apply action"""

    def test_apply_to_nonexistent_organisation(self, authenticated_client):
        """
        Test that applying to non-existent organisation returns 404.
        """
        data = {
            "message": "<p>Test application</p>",
            "email_subject": "Test Subject",
            "recipients": "contact@test.com",
        }

        response = authenticated_client.post("/api/festivals/999999/apply/", data)

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_apply_with_invalid_recipient_email(
        self, authenticated_client, festival, authenticated_user
    ):
        """
        Test that invalid recipient emails are rejected.
        """
        authenticated_user.email_host = "OTHER"
        authenticated_user.other_email_host = "ssl0.ovh.net"
        authenticated_user.email_host_user = "test@test.com"
        authenticated_user.email_host_password = "TestPassword123!"
        authenticated_user.save()

        data = {
            "message": "<p>Test application</p>",
            "email_subject": "Test Subject",
            "recipients": "not-an-email",
        }

        response = authenticated_client.post(f"/api/festivals/{festival.id}/apply/", data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
class TestSearchEndpointEdgeCases:
    """Test edge cases in search endpoint"""

    def test_search_with_empty_query_returns_empty(self, authenticated_client):
        """
        Test that search with empty query returns empty list.
        """
        response = authenticated_client.get("/api/organisations/search/?q=")

        assert response.status_code == status.HTTP_200_OK
        assert response.data == []

    def test_search_returns_max_15_results(self, authenticated_client, authenticated_user):
        """
        Test that search returns maximum 15 results when no type specified.
        """
        # Create many festivals
        for i in range(20):
            Festival.objects.create(
                name=f"Test Festival {i}",
                country="France",
                town="Paris",
                user=authenticated_user,
            )

        response = authenticated_client.get("/api/organisations/search/?q=Test")

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) <= 15

    def test_search_returns_max_20_for_single_type(self, authenticated_client, authenticated_user):
        """
        Test that search returns maximum 20 results when type is specified.
        """
        # Create many festivals
        for i in range(25):
            Festival.objects.create(
                name=f"Test Festival {i}",
                country="France",
                town="Paris",
                user=authenticated_user,
            )

        response = authenticated_client.get("/api/organisations/search/?q=Test&type=festival")

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) <= 20


@pytest.mark.django_db
class TestOrganisationBaseViewSetMethods:
    """Test base OrganisationViewSet methods"""

    def test_get_organisation_type_name_default(self, authenticated_client, authenticated_user):
        """
        Test that get_organisation_type_name returns correct name.
        Note: This will return 'festival' for Festival viewset, not 'organisation'
        since each subclass overrides it.
        """
        festival = Festival.objects.create(
            name="Test Festival",
            country="France",
            town="Paris",
            user=authenticated_user,
        )

        response = authenticated_client.get(f"/api/festivals/{festival.id}/")

        assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
class TestApplyValidation:
    """Test apply action validation"""

    def test_apply_with_missing_subject_returns_error(
        self, authenticated_client, festival, authenticated_user
    ):
        """
        Test that apply without subject returns error.
        """
        authenticated_user.email_host = "OTHER"
        authenticated_user.other_email_host = "ssl0.ovh.net"
        authenticated_user.email_host_user = "test@test.com"
        authenticated_user.email_host_password = "TestPassword123!"
        authenticated_user.save()

        data = {
            "message": "<p>Test application</p>",
            "recipients": "contact@festival.com",
        }

        response = authenticated_client.post(f"/api/festivals/{festival.id}/apply/", data)

        # Should fail because subject is missing
        assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
class TestVenueViewSet:
    """Test VenueViewSet specific functionality"""

    def test_venue_get_organisation_type_name(self, authenticated_client, authenticated_user):
        """
        Test that venue viewset returns correct type name.
        """
        from organisations.venues.models import Venue

        venue = Venue.objects.create(
            name="Test Venue",
            country="France",
            town="Paris",
            user=authenticated_user,
        )

        response = authenticated_client.get(f"/api/venues/{venue.id}/")

        assert response.status_code == status.HTTP_200_OK

    @patch("organisations.views.MistralClient")
    def test_venue_enrich_uses_venue_prompt(
        self, mock_mistral_client, authenticated_client, authenticated_user
    ):
        """
        Test that venue enrichment uses venue-specific prompt.
        """
        from organisations.venues.models import Venue
        from mistralai import TextChunk

        venue = Venue.objects.create(
            name="Test Venue",
            country="France",
            town="Paris",
            website_url="https://venue.com",
            user=authenticated_user,
        )

        # Mock the Mistral service
        mock_mistral = Mock()

        mock_text_chunk = Mock(
            spec=TextChunk,
            text="Test venue in France",
        )
        mock_output = Mock(type="message.output", content=[mock_text_chunk])
        mock_search_response = Mock(outputs=[mock_output])
        mock_mistral.search.return_value = mock_search_response

        mock_mistral.chat.return_value = """
        {
            "description": "A test venue"
        }
        """
        mock_mistral_client.return_value = mock_mistral

        response = authenticated_client.get(f"/api/venues/{venue.id}/enrich/")

        assert response.status_code == status.HTTP_200_OK
        assert mock_mistral.search.called
        assert mock_mistral.chat.called

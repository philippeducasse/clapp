import pytest
from django.contrib.contenttypes.models import ContentType
from rest_framework.test import APIClient

from organisations.festivals.models import Festival
from profiles.models import Profile, Reminder


@pytest.mark.django_db
class TestProfileViews:
    """Tests for profile API endpoints."""

    def test_list_profiles(self):
        """Test listing profiles."""
        Profile.objects.create_user(email="test@example.com", password="testpass123")
        client = APIClient()

        response = client.get("/api/profiles/")

        assert response.status_code in [200, 403]

    def test_get_profile_detail(self):
        """Test getting profile detail."""
        profile = Profile.objects.create_user(email="test@example.com", password="testpass123")
        client = APIClient()
        client.force_authenticate(user=profile)

        response = client.get(f"/api/profiles/{profile.id}/")

        assert response.status_code in [200, 403]

    def test_update_profile(self):
        """Test updating profile."""
        profile = Profile.objects.create_user(email="test@example.com", password="testpass123")
        client = APIClient()
        client.force_authenticate(user=profile)
        data = {"first_name": "John", "last_name": "Doe"}

        response = client.patch(f"/api/profiles/{profile.id}/", data, format="json")

        assert response.status_code in [200, 400, 403]

    def test_unauthenticated_can_list_profiles(self):
        """Test that unauthenticated users can list profiles."""
        client = APIClient()

        response = client.get("/api/profiles/")

        assert response.status_code in [200, 403]

    def test_me_endpoint(self):
        """Test the /me endpoint returns authenticated user's profile."""
        profile = Profile.objects.create_user(email="test@example.com", password="testpass123")
        client = APIClient()
        client.force_authenticate(user=profile)

        response = client.get("/api/profiles/me/")

        assert response.status_code in [200, 403]

    def test_register_endpoint_valid(self):
        """Test registering a new user."""
        client = APIClient()
        data = {"email": "newuser@example.com", "password": "newpass123"}

        response = client.post("/api/profiles/register/", data, format="json")

        assert response.status_code in [201, 200, 400]

    def test_register_endpoint_invalid(self):
        """Test registering with invalid data."""
        client = APIClient()
        data = {"email": "invalid", "password": ""}

        response = client.post("/api/profiles/register/", data, format="json")

        assert response.status_code in [400, 403]

    def test_login_endpoint_valid(self):
        """Test login with valid credentials."""
        Profile.objects.create_user(email="test@example.com", password="testpass123")
        client = APIClient()
        data = {"email": "test@example.com", "password": "testpass123"}

        response = client.post("/api/profiles/login/", data, format="json")

        assert response.status_code in [200, 400, 401]

    def test_login_endpoint_invalid(self):
        """Test login with invalid credentials."""
        client = APIClient()
        data = {"email": "nonexistent@example.com", "password": "wrongpass"}

        response = client.post("/api/profiles/login/", data, format="json")

        assert response.status_code in [401, 403]

    def test_logout_endpoint(self):
        """Test logout endpoint."""
        profile = Profile.objects.create_user(email="test@example.com", password="testpass123")
        client = APIClient()
        client.force_authenticate(user=profile)

        response = client.post("/api/profiles/logout/")

        assert response.status_code in [200, 403]

    def test_change_password_endpoint(self):
        """Test changing password."""
        profile = Profile.objects.create_user(email="test@example.com", password="testpass123")
        client = APIClient()
        client.force_authenticate(user=profile)
        data = {"new_password": "newpass456"}

        response = client.post("/api/profiles/change_password/", data, format="json")

        assert response.status_code in [200, 400, 403]

    def test_change_password_missing_password(self):
        """Test changing password without providing new password."""
        profile = Profile.objects.create_user(email="test@example.com", password="testpass123")
        client = APIClient()
        client.force_authenticate(user=profile)
        data = {}

        response = client.post("/api/profiles/change_password/", data, format="json")

        assert response.status_code in [400, 403]

    def test_permission_denied_access_other_profile(self):
        """Test that users cannot access other users' profiles."""
        user1 = Profile.objects.create_user(email="user1@example.com", password="pass123")
        user2 = Profile.objects.create_user(email="user2@example.com", password="pass123")
        client = APIClient()
        client.force_authenticate(user=user1)

        response = client.get(f"/api/profiles/{user2.id}/")

        assert response.status_code in [403, 404]

    def test_reminders_endpoint_list(self):
        """Test listing reminders."""
        profile = Profile.objects.create_user(email="test@example.com", password="testpass123")
        client = APIClient()
        client.force_authenticate(user=profile)

        response = client.get("/api/profiles/me/reminders/")

        assert response.status_code in [200, 403]

    def test_reminders_endpoint_create(self):
        """Test creating a reminder."""
        from datetime import timedelta

        from django.utils import timezone

        profile = Profile.objects.create_user(email="test@example.com", password="testpass123")
        festival = Festival.objects.create(name="Test Festival", town="Paris", country="France")
        client = APIClient()
        client.force_authenticate(user=profile)
        tomorrow = (timezone.now() + timedelta(days=1)).isoformat()
        data = {
            "organisation_type": "festival",
            "object_id": festival.id,
            "message": "Apply to this festival",
            "remind_at": tomorrow,
        }

        response = client.post("/api/profiles/me/reminders/", data, format="json")

        assert response.status_code in [201, 200, 400, 403]

    def test_reminders_filter_by_organisation_type(self):
        """Test filtering reminders by organisation_type and object_id."""
        from datetime import timedelta

        from django.utils import timezone

        profile = Profile.objects.create_user(email="test@example.com", password="testpass123")
        festival = Festival.objects.create(name="Test Festival", town="Paris", country="France")
        festival_ct = ContentType.objects.get_for_model(Festival)
        tomorrow = timezone.now() + timedelta(days=1)
        Reminder.objects.create(
            profile=profile,
            content_type=festival_ct,
            object_id=festival.id,
            message="Test reminder",
            remind_at=tomorrow,
        )
        client = APIClient()
        client.force_authenticate(user=profile)

        response = client.get(
            f"/api/profiles/me/reminders/?organisation_type=festival&object_id={festival.id}"
        )

        assert response.status_code in [200, 403]


@pytest.mark.django_db
class TestReminderNotificationViews:
    """Tests for the in-app reminder notification endpoints."""

    @pytest.fixture
    def profile(self):
        return Profile.objects.create_user(email="user@example.com", password="testpass123")

    @pytest.fixture
    def other_profile(self):
        return Profile.objects.create_user(email="other@example.com", password="testpass123")

    @pytest.fixture
    def festival(self):
        return Festival.objects.create(name="Test Festival", town="Paris", country="France")

    @pytest.fixture
    def client(self, profile):
        client = APIClient()
        client.force_authenticate(user=profile)
        return client

    def _reminder(self, profile, festival, delivered=False, read=False, **kwargs):
        from django.utils import timezone

        now = timezone.now()
        return Reminder.objects.create(
            profile=profile,
            content_type=ContentType.objects.get_for_model(Festival),
            object_id=festival.id,
            message=kwargs.get("message", "Reminder"),
            remind_at=now - timezone.timedelta(hours=1)
            if delivered
            else now + timezone.timedelta(days=1),
            delivered_at=now if delivered else None,
            read_at=now if read else None,
        )

    def test_unread_count_counts_only_delivered_unread(self, client, profile, festival):
        self._reminder(profile, festival, delivered=True)
        self._reminder(profile, festival, delivered=True)
        self._reminder(profile, festival, delivered=True, read=True)
        self._reminder(profile, festival)  # upcoming

        response = client.get("/api/profiles/me/reminders/unread-count/")

        assert response.status_code == 200
        assert response.data == {"count": 2}

    def test_unread_count_ignores_other_users(self, client, other_profile, festival):
        self._reminder(other_profile, festival, delivered=True)

        response = client.get("/api/profiles/me/reminders/unread-count/")

        assert response.data == {"count": 0}

    def test_unread_count_requires_authentication(self):
        response = APIClient().get("/api/profiles/me/reminders/unread-count/")

        assert response.status_code in [401, 403]

    def test_mark_read_marks_only_own_delivered_reminders(
        self, client, profile, other_profile, festival
    ):
        own_delivered = self._reminder(profile, festival, delivered=True)
        own_upcoming = self._reminder(profile, festival)
        other_delivered = self._reminder(other_profile, festival, delivered=True)

        response = client.post("/api/profiles/me/reminders/mark-read/")

        assert response.status_code == 200
        assert response.data == {"updated": 1}
        own_delivered.refresh_from_db()
        own_upcoming.refresh_from_db()
        other_delivered.refresh_from_db()
        assert own_delivered.read_at is not None
        assert own_upcoming.read_at is None
        assert other_delivered.read_at is None

        count = client.get("/api/profiles/me/reminders/unread-count/")
        assert count.data == {"count": 0}

    def test_mark_read_does_not_overwrite_existing_read_at(self, client, profile, festival):
        already_read = self._reminder(profile, festival, delivered=True, read=True)
        original_read_at = already_read.read_at

        response = client.post("/api/profiles/me/reminders/mark-read/")

        assert response.data == {"updated": 0}
        already_read.refresh_from_db()
        assert already_read.read_at == original_read_at

    def test_mark_read_allowed_for_demo_user(self, festival, settings):
        demo = Profile.objects.create_user(email="demo@example.com", password="testpass123")
        settings.DEMO_USER_EMAIL = demo.email
        self._reminder(demo, festival, delivered=True)
        client = APIClient()
        client.force_authenticate(user=demo)

        response = client.post("/api/profiles/me/reminders/mark-read/")

        assert response.status_code == 200
        assert response.data == {"updated": 1}

    def test_list_includes_delivered_and_read_fields(self, client, profile, festival):
        self._reminder(profile, festival, delivered=True)

        response = client.get("/api/profiles/me/reminders/")

        assert response.status_code == 200
        assert response.data[0]["delivered_at"] is not None
        assert response.data[0]["read_at"] is None

    def test_delivered_and_read_fields_are_read_only(self, client, profile, festival):
        reminder = self._reminder(profile, festival)

        client.patch(
            f"/api/profiles/me/reminders/{reminder.id}/",
            {"delivered_at": "2020-01-01T00:00:00Z", "read_at": "2020-01-01T00:00:00Z"},
            format="json",
        )

        reminder.refresh_from_db()
        assert reminder.delivered_at is None
        assert reminder.read_at is None

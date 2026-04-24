import pytest
from django.test import override_settings
from rest_framework.test import APIRequestFactory

from profiles.models import Profile
from profiles.permissions import IsNotDemoUser


@pytest.mark.django_db
class TestIsNotDemoUserPermission:
    """Tests for IsNotDemoUser permission class."""

    def test_demo_user_allowed_for_get_request(self):
        """Demo user is allowed to make GET requests."""
        demo_user = Profile.objects.create_user(email="demo@clapp.ovh", password="testpass123")
        factory = APIRequestFactory()
        request = factory.get("/api/festivals/")
        request.user = demo_user
        permission = IsNotDemoUser()

        assert permission.has_permission(request, None) is True

    def test_demo_user_allowed_for_head_request(self):
        """Demo user is allowed to make HEAD requests."""
        demo_user = Profile.objects.create_user(email="demo@clapp.ovh", password="testpass123")
        factory = APIRequestFactory()
        request = factory.head("/api/festivals/")
        request.user = demo_user
        permission = IsNotDemoUser()

        assert permission.has_permission(request, None) is True

    def test_demo_user_allowed_for_options_request(self):
        """Demo user is allowed to make OPTIONS requests."""
        demo_user = Profile.objects.create_user(email="demo@clapp.ovh", password="testpass123")
        factory = APIRequestFactory()
        request = factory.options("/api/festivals/")
        request.user = demo_user
        permission = IsNotDemoUser()

        assert permission.has_permission(request, None) is True

    def test_demo_user_denied_for_post_request(self):
        """Demo user is denied POST requests."""
        demo_user = Profile.objects.create_user(email="demo@clapp.ovh", password="testpass123")
        factory = APIRequestFactory()
        request = factory.post("/api/festivals/")
        request.user = demo_user
        permission = IsNotDemoUser()

        assert permission.has_permission(request, None) is False

    def test_demo_user_denied_for_put_request(self):
        """Demo user is denied PUT requests."""
        demo_user = Profile.objects.create_user(email="demo@clapp.ovh", password="testpass123")
        factory = APIRequestFactory()
        request = factory.put("/api/festivals/1/")
        request.user = demo_user
        permission = IsNotDemoUser()

        assert permission.has_permission(request, None) is False

    def test_demo_user_denied_for_patch_request(self):
        """Demo user is denied PATCH requests."""
        demo_user = Profile.objects.create_user(email="demo@clapp.ovh", password="testpass123")
        factory = APIRequestFactory()
        request = factory.patch("/api/festivals/1/")
        request.user = demo_user
        permission = IsNotDemoUser()

        assert permission.has_permission(request, None) is False

    def test_demo_user_denied_for_delete_request(self):
        """Demo user is denied DELETE requests."""
        demo_user = Profile.objects.create_user(email="demo@clapp.ovh", password="testpass123")
        factory = APIRequestFactory()
        request = factory.delete("/api/festivals/1/")
        request.user = demo_user
        permission = IsNotDemoUser()

        assert permission.has_permission(request, None) is False

    def test_regular_user_allowed_for_post_request(self):
        """Regular user is allowed POST requests."""
        user = Profile.objects.create_user(email="user@example.com", password="testpass123")
        factory = APIRequestFactory()
        request = factory.post("/api/festivals/")
        request.user = user
        permission = IsNotDemoUser()

        assert permission.has_permission(request, None) is True

    def test_regular_user_allowed_for_put_request(self):
        """Regular user is allowed PUT requests."""
        user = Profile.objects.create_user(email="user@example.com", password="testpass123")
        factory = APIRequestFactory()
        request = factory.put("/api/festivals/1/")
        request.user = user
        permission = IsNotDemoUser()

        assert permission.has_permission(request, None) is True

    def test_regular_user_allowed_for_patch_request(self):
        """Regular user is allowed PATCH requests."""
        user = Profile.objects.create_user(email="user@example.com", password="testpass123")
        factory = APIRequestFactory()
        request = factory.patch("/api/festivals/1/")
        request.user = user
        permission = IsNotDemoUser()

        assert permission.has_permission(request, None) is True

    def test_regular_user_allowed_for_delete_request(self):
        """Regular user is allowed DELETE requests."""
        user = Profile.objects.create_user(email="user@example.com", password="testpass123")
        factory = APIRequestFactory()
        request = factory.delete("/api/festivals/1/")
        request.user = user
        permission = IsNotDemoUser()

        assert permission.has_permission(request, None) is True

    def test_regular_user_allowed_for_get_request(self):
        """Regular user is allowed GET requests."""
        user = Profile.objects.create_user(email="user@example.com", password="testpass123")
        factory = APIRequestFactory()
        request = factory.get("/api/festivals/")
        request.user = user
        permission = IsNotDemoUser()

        assert permission.has_permission(request, None) is True

    @override_settings(DEMO_USER_EMAIL="custom@demo.ovh")
    def test_custom_demo_user_email_setting(self):
        """Permission respects custom DEMO_USER_EMAIL setting."""
        custom_demo_user = Profile.objects.create_user(
            email="custom@demo.ovh", password="testpass123"
        )
        factory = APIRequestFactory()
        request = factory.post("/api/festivals/")
        request.user = custom_demo_user
        permission = IsNotDemoUser()

        assert permission.has_permission(request, None) is False

    @override_settings(DEMO_USER_EMAIL="custom@demo.ovh")
    def test_user_with_different_email_not_blocked(self):
        """Non-demo user with different email can make write requests."""
        user = Profile.objects.create_user(email="regular@example.com", password="testpass123")
        factory = APIRequestFactory()
        request = factory.post("/api/festivals/")
        request.user = user
        permission = IsNotDemoUser()

        assert permission.has_permission(request, None) is True

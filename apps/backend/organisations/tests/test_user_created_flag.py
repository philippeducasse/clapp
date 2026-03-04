"""
Tests for OrganisationSerializerMixin and the is_user_created / added_by fields.

An organisation falls into one of three states:
  1. Seed template  — user=None, is_seed_clone=False
                      (global template, cloned for new users on registration)
  2. Seed clone     — user=<someone>, is_seed_clone=True
                      (a copy given to a user during registration; treated as
                      "seed-like", private to that user)
  3. User-created   — user=<someone>, is_seed_clone=False
                      (genuinely added by the user via the API)

Expected field values per state:
  | State          | is_user_created | added_by        |
  |----------------|-----------------|-----------------|
  | Seed template  | False           | None            |
  | Seed clone     | False           | None            |
  | User-created   | True            | owner's email   |

The feature is implemented in OrganisationSerializerMixin (shared across
Festival, Venue and Residency) and relies on select_related("user") in
OrganisationViewSet.get_queryset to avoid N+1 queries.
"""

from unittest.mock import Mock

import pytest
from rest_framework.test import APIClient

from organisations.festivals.models import Festival
from organisations.residencies.models import Residency
from organisations.serializers import OrganisationSerializerMixin
from organisations.venues.models import Venue
from profiles.models import Profile


# ============================================================================
# SHARED FIXTURES
# ============================================================================


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def regular_user(db):
    return Profile.objects.create_user(
        email="user@example.com",
        password="testpass123",
    )


@pytest.fixture
def other_user(db):
    """A second regular user — used to verify that admins see their email in added_by."""
    return Profile.objects.create_user(
        email="other@example.com",
        password="testpass123",
    )


@pytest.fixture
def admin_user(db):
    return Profile.objects.create_user(
        email="admin@example.com",
        password="testpass123",
        is_staff=True,
    )


# ============================================================================
# UNIT TESTS — mixin logic in isolation (no DB, no HTTP)
# ============================================================================


class TestOrganisationSerializerMixinLogic:
    """Unit tests for get_is_user_created and get_added_by.

    These call the mixin methods directly with a lightweight mock object so
    the tests stay fast and don't touch the database. The three cases map
    exactly to the three organisation states described at the top of this file.
    """

    def _make_obj(self, user_id, email, is_seed_clone):
        """Build a minimal mock that the mixin methods can introspect."""
        obj = Mock()
        obj.user_id = user_id
        obj.is_seed_clone = is_seed_clone
        if user_id is not None:
            obj.user = Mock()
            obj.user.email = email
        return obj

    # — is_user_created ---------------------------------------------------------

    def test_seed_template_is_not_user_created(self):
        """Seed templates (user=None) are never user-created."""
        mixin = OrganisationSerializerMixin()
        obj = self._make_obj(user_id=None, email=None, is_seed_clone=False)
        assert mixin.get_is_user_created(obj) is False

    def test_seed_clone_is_not_user_created(self):
        """Seed clones (is_seed_clone=True) are treated as seed-like, not user-created."""
        mixin = OrganisationSerializerMixin()
        obj = self._make_obj(user_id=1, email="u@example.com", is_seed_clone=True)
        assert mixin.get_is_user_created(obj) is False

    def test_user_created_org_is_user_created(self):
        """Orgs with a user and is_seed_clone=False are user-created."""
        mixin = OrganisationSerializerMixin()
        obj = self._make_obj(user_id=1, email="u@example.com", is_seed_clone=False)
        assert mixin.get_is_user_created(obj) is True

    # — added_by ----------------------------------------------------------------

    def test_seed_template_has_no_added_by(self):
        mixin = OrganisationSerializerMixin()
        obj = self._make_obj(user_id=None, email=None, is_seed_clone=False)
        assert mixin.get_added_by(obj) is None

    def test_seed_clone_has_no_added_by(self):
        mixin = OrganisationSerializerMixin()
        obj = self._make_obj(user_id=1, email="u@example.com", is_seed_clone=True)
        assert mixin.get_added_by(obj) is None

    def test_user_created_added_by_returns_owner_email(self):
        mixin = OrganisationSerializerMixin()
        obj = self._make_obj(user_id=1, email="creator@example.com", is_seed_clone=False)
        assert mixin.get_added_by(obj) == "creator@example.com"


# ============================================================================
# API TESTS — field values in HTTP responses
# ============================================================================
#
# Each org type gets its own class so failures are easy to locate.
# Only the seed-template scenario requires an admin (regular users can't see
# seed templates). The other scenarios are tested as the owning regular user.


@pytest.mark.django_db
class TestFestivalUserCreatedFields:
    """is_user_created and added_by in festival list / detail responses."""

    def test_seed_template_fields_via_admin(self, api_client, admin_user):
        """Seed template (user=None): both fields falsy."""
        Festival.objects.create(name="SeedFestival", country="XX", user=None, is_seed_clone=False)

        api_client.force_authenticate(user=admin_user)
        response = api_client.get("/api/festivals/")

        result = next(f for f in response.data["results"] if f["name"] == "SeedFestival")
        assert result["is_user_created"] is False
        assert result["added_by"] is None

    def test_seed_clone_fields(self, api_client, regular_user):
        """Seed clone (is_seed_clone=True): both fields falsy."""
        Festival.objects.create(
            name="CloneFestival", country="FR", user=regular_user, is_seed_clone=True
        )

        api_client.force_authenticate(user=regular_user)
        response = api_client.get("/api/festivals/")

        result = response.data["results"][0]
        assert result["is_user_created"] is False
        assert result["added_by"] is None

    def test_user_created_fields(self, api_client, regular_user):
        """User-created festival: is_user_created=True, added_by=owner email."""
        Festival.objects.create(
            name="MyFestival", country="FR", user=regular_user, is_seed_clone=False
        )

        api_client.force_authenticate(user=regular_user)
        response = api_client.get("/api/festivals/")

        result = response.data["results"][0]
        assert result["is_user_created"] is True
        assert result["added_by"] == regular_user.email

    def test_admin_sees_other_users_email_in_added_by(self, api_client, admin_user, other_user):
        """Admin viewing another user's festival sees that user's email in added_by."""
        Festival.objects.create(
            name="OtherUserFestival", country="DE", user=other_user, is_seed_clone=False
        )

        api_client.force_authenticate(user=admin_user)
        response = api_client.get("/api/festivals/")

        result = next(f for f in response.data["results"] if f["name"] == "OtherUserFestival")
        assert result["is_user_created"] is True
        assert result["added_by"] == other_user.email

    def test_fields_present_on_detail_endpoint(self, api_client, regular_user):
        """The fields are also present on the detail (retrieve) endpoint."""
        festival = Festival.objects.create(
            name="DetailFestival", country="ES", user=regular_user, is_seed_clone=False
        )

        api_client.force_authenticate(user=regular_user)
        response = api_client.get(f"/api/festivals/{festival.id}/")

        assert "is_user_created" in response.data
        assert "added_by" in response.data
        assert response.data["is_user_created"] is True
        assert response.data["added_by"] == regular_user.email


@pytest.mark.django_db
class TestVenueUserCreatedFields:
    """is_user_created and added_by in venue API responses."""

    def test_seed_clone_fields(self, api_client, regular_user):
        Venue.objects.create(
            name="VenueClone", country="FR", user=regular_user, is_seed_clone=True
        )

        api_client.force_authenticate(user=regular_user)
        response = api_client.get("/api/venues/")

        result = response.data["results"][0]
        assert result["is_user_created"] is False
        assert result["added_by"] is None

    def test_user_created_fields(self, api_client, regular_user):
        Venue.objects.create(
            name="MyVenue", country="ES", user=regular_user, is_seed_clone=False
        )

        api_client.force_authenticate(user=regular_user)
        response = api_client.get("/api/venues/")

        result = response.data["results"][0]
        assert result["is_user_created"] is True
        assert result["added_by"] == regular_user.email

    def test_admin_sees_other_users_email_in_added_by(self, api_client, admin_user, other_user):
        Venue.objects.create(
            name="OtherUserVenue", country="IT", user=other_user, is_seed_clone=False
        )

        api_client.force_authenticate(user=admin_user)
        response = api_client.get("/api/venues/")

        result = next(v for v in response.data["results"] if v["name"] == "OtherUserVenue")
        assert result["is_user_created"] is True
        assert result["added_by"] == other_user.email


@pytest.mark.django_db
class TestResidencyUserCreatedFields:
    """is_user_created and added_by in residency API responses."""

    def test_seed_clone_fields(self, api_client, regular_user):
        Residency.objects.create(
            name="ResidencyClone", country="BE", user=regular_user, is_seed_clone=True
        )

        api_client.force_authenticate(user=regular_user)
        response = api_client.get("/api/residencies/")

        result = response.data["results"][0]
        assert result["is_user_created"] is False
        assert result["added_by"] is None

    def test_user_created_fields(self, api_client, regular_user):
        Residency.objects.create(
            name="MyResidency", country="NL", user=regular_user, is_seed_clone=False
        )

        api_client.force_authenticate(user=regular_user)
        response = api_client.get("/api/residencies/")

        result = response.data["results"][0]
        assert result["is_user_created"] is True
        assert result["added_by"] == regular_user.email

    def test_admin_sees_other_users_email_in_added_by(self, api_client, admin_user, other_user):
        Residency.objects.create(
            name="OtherUserResidency", country="PT", user=other_user, is_seed_clone=False
        )

        api_client.force_authenticate(user=admin_user)
        response = api_client.get("/api/residencies/")

        result = next(r for r in response.data["results"] if r["name"] == "OtherUserResidency")
        assert result["is_user_created"] is True
        assert result["added_by"] == other_user.email
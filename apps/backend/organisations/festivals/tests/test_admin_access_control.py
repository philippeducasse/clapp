"""
Comprehensive tests for admin access control and seed clone functionality.

This test module verifies the role-based visibility system for organisations:

VISIBILITY RULES:
- Regular users: See ONLY their own organisations (both seeded + created)
- Admin staff: See their own organisations + all user-created organisations from other users
- Admin staff do NOT see other users' seed-cloned organisations

SEED CLONE BEHAVIOR:
- When user creates org via API: is_seed_clone=False (default)
- When org is cloned during registration: is_seed_clone=True
- Seed organisations (user=NULL) are templates, not directly visible to any user

These tests serve as executable specification for the feature and ensure:
1. Data isolation between regular users
2. Appropriate admin visibility for support/debugging
3. Privacy protection of seeded data (don't expose other users' defaults)
4. Correct tagging of organisations as seed clones vs user-created
"""

import pytest
from rest_framework import status
from rest_framework.test import APIClient

from organisations.festivals.models import Festival
from profiles.models import Profile

# ============================================================================
# FIXTURES
# ============================================================================


@pytest.fixture
def api_client():
    """Fixture to provide an API client."""
    return APIClient()


@pytest.fixture
def user1(db):
    """
    Regular user 1 (non-staff).

    This user will have:
    - Seed-cloned organisations (is_seed_clone=True)
    - User-created organisations (is_seed_clone=False)
    """
    user = Profile.objects.create_user(
        email="user1@example.com",
        password="testpass123",
        first_name="User",
        last_name="One",
        is_staff=False,
    )
    return user


@pytest.fixture
def user2(db):
    """
    Regular user 2 (non-staff).

    This user will have:
    - Seed-cloned organisations (is_seed_clone=True)
    - User-created organisations (is_seed_clone=False)
    """
    user = Profile.objects.create_user(
        email="user2@example.com",
        password="testpass123",
        first_name="User",
        last_name="Two",
        is_staff=False,
    )
    return user


@pytest.fixture
def admin_user(db):
    """
    Admin staff user.

    This user should see:
    - Their own organisations (both seeded and created)
    - All user-created organisations from other users (is_seed_clone=False, user!=None)

    This user should NOT see:
    - Other users' seed-cloned organisations (is_seed_clone=True, user!=self)
    - Seed template organisations (user=None)
    """
    user = Profile.objects.create_user(
        email="admin@example.com",
        password="adminpass123",
        first_name="Admin",
        last_name="User",
        is_staff=True,
    )
    return user


@pytest.fixture
def seed_template_festival(db):
    """
    Seed template festival (user=NULL).

    This represents the base template that gets cloned for new users.
    Should never be visible in any user's festival list.
    """
    return Festival.objects.create(
        name="Seed Template Festival",
        description="Template for new users",
        country="Global",
        town="Template",
        festival_type="CIRCUS",
        user=None,  # No user = template
        is_seed_clone=False,  # Templates are not clones
    )


@pytest.fixture
def user1_seeded_festival(user1):
    """
    Festival cloned from template during user1's registration.

    Characteristics:
    - user=user1
    - is_seed_clone=True (cloned from template during registration)
    - Should be visible ONLY to user1
    - Should NOT be visible to admin (privacy protection)
    """
    return Festival.objects.create(
        name="User1 Seeded Festival",
        description="Cloned during registration",
        country="France",
        town="Paris",
        festival_type="STREET",
        user=user1,
        is_seed_clone=True,  # Cloned during registration
    )


@pytest.fixture
def user1_created_festival(user1):
    """
    Festival created by user1 via API.

    Characteristics:
    - user=user1
    - is_seed_clone=False (user-created)
    - Should be visible to user1
    - Should be visible to admin (user-created content)
    """
    return Festival.objects.create(
        name="User1 Created Festival",
        description="Created by user1",
        country="Spain",
        town="Barcelona",
        festival_type="CIRCUS",
        user=user1,
        is_seed_clone=False,  # User-created
    )


@pytest.fixture
def user2_seeded_festival(user2):
    """
    Festival cloned from template during user2's registration.

    Characteristics:
    - user=user2
    - is_seed_clone=True
    - Should be visible ONLY to user2
    - Should NOT be visible to admin or user1
    """
    return Festival.objects.create(
        name="User2 Seeded Festival",
        description="Cloned during registration",
        country="Germany",
        town="Berlin",
        festival_type="THEATRE",
        user=user2,
        is_seed_clone=True,
    )


@pytest.fixture
def user2_created_festival(user2):
    """
    Festival created by user2 via API.

    Characteristics:
    - user=user2
    - is_seed_clone=False
    - Should be visible to user2
    - Should be visible to admin (user-created content)
    """
    return Festival.objects.create(
        name="User2 Created Festival",
        description="Created by user2",
        country="Italy",
        town="Rome",
        festival_type="MUSIC",
        user=user2,
        is_seed_clone=False,
    )


@pytest.fixture
def admin_seeded_festival(admin_user):
    """
    Festival cloned from template during admin's registration.

    Characteristics:
    - user=admin_user
    - is_seed_clone=True
    - Should be visible to admin
    """
    return Festival.objects.create(
        name="Admin Seeded Festival",
        description="Cloned during admin registration",
        country="UK",
        town="London",
        festival_type="DANCE",
        user=admin_user,
        is_seed_clone=True,
    )


@pytest.fixture
def admin_created_festival(admin_user):
    """
    Festival created by admin via API.

    Characteristics:
    - user=admin_user
    - is_seed_clone=False
    - Should be visible to admin
    """
    return Festival.objects.create(
        name="Admin Created Festival",
        description="Created by admin",
        country="Netherlands",
        town="Amsterdam",
        festival_type="OTHER",
        user=admin_user,
        is_seed_clone=False,
    )


# ============================================================================
# REGULAR USER ACCESS CONTROL TESTS
# ============================================================================


@pytest.mark.django_db
class TestRegularUserAccessControl:
    """
    Test suite for regular (non-staff) user visibility.

    Regular users should see ONLY their own organisations, regardless of
    whether they are seed-cloned or user-created.
    """

    def test_user1_sees_only_own_festivals(
        self,
        api_client,
        user1,
        user1_seeded_festival,
        user1_created_festival,
        user2_seeded_festival,
        user2_created_festival,
        seed_template_festival,
    ):
        """
        Regular user sees only their own organisations.

        User1 should see:
        - user1_seeded_festival (their own, seeded)
        - user1_created_festival (their own, created)

        User1 should NOT see:
        - user2_seeded_festival (other user's seeded)
        - user2_created_festival (other user's created)
        - seed_template_festival (template with user=NULL)
        """
        api_client.force_authenticate(user=user1)
        response = api_client.get("/api/festivals/")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 2, (
            "User1 should see exactly 2 festivals (own seeded + created)"
        )

        festival_names = {festival["name"] for festival in response.data["results"]}
        assert "User1 Seeded Festival" in festival_names, "User should see their seeded festival"
        assert "User1 Created Festival" in festival_names, "User should see their created festival"
        assert "User2 Seeded Festival" not in festival_names, (
            "User should NOT see other user's seeded festival"
        )
        assert "User2 Created Festival" not in festival_names, (
            "User should NOT see other user's created festival"
        )
        assert "Seed Template Festival" not in festival_names, (
            "User should NOT see template festivals"
        )

    def test_user2_sees_only_own_festivals(
        self,
        api_client,
        user2,
        user1_seeded_festival,
        user1_created_festival,
        user2_seeded_festival,
        user2_created_festival,
    ):
        """
        Regular user sees only their own organisations (verification with user2).

        User2 should see:
        - user2_seeded_festival (their own, seeded)
        - user2_created_festival (their own, created)

        User2 should NOT see:
        - user1_seeded_festival (other user's seeded)
        - user1_created_festival (other user's created)
        """
        api_client.force_authenticate(user=user2)
        response = api_client.get("/api/festivals/")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 2, (
            "User2 should see exactly 2 festivals (own seeded + created)"
        )

        festival_names = {festival["name"] for festival in response.data["results"]}
        assert "User2 Seeded Festival" in festival_names
        assert "User2 Created Festival" in festival_names
        assert "User1 Seeded Festival" not in festival_names
        assert "User1 Created Festival" not in festival_names

    def test_regular_user_cannot_access_other_user_festival_by_id(
        self,
        api_client,
        user1,
        user2_created_festival,
    ):
        """
        Regular user cannot access another user's festival by direct ID lookup.

        Even if user1 knows the ID of user2's festival, they should not be
        able to retrieve it (404 response).
        """
        api_client.force_authenticate(user=user1)
        response = api_client.get(f"/api/festivals/{user2_created_festival.id}/")

        assert response.status_code == status.HTTP_404_NOT_FOUND, (
            "User should get 404 when trying to access another user's festival"
        )

    def test_regular_user_cannot_modify_other_user_festival(
        self,
        api_client,
        user1,
        user2_created_festival,
    ):
        """
        Regular user cannot modify another user's festival.

        User1 should not be able to update user2's festival.
        """
        api_client.force_authenticate(user=user1)
        response = api_client.patch(
            f"/api/festivals/{user2_created_festival.id}/",
            {"name": "Hacked Name"},
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND, (
            "User should get 404 when trying to modify another user's festival"
        )

        # Verify the festival was not modified
        user2_created_festival.refresh_from_db()
        assert user2_created_festival.name == "User2 Created Festival", (
            "Festival name should not have been changed"
        )

    def test_regular_user_cannot_delete_other_user_festival(
        self,
        api_client,
        user1,
        user2_created_festival,
    ):
        """
        Regular user cannot delete another user's festival.

        User1 should not be able to delete user2's festival.
        """
        api_client.force_authenticate(user=user1)
        festival_id = user2_created_festival.id
        response = api_client.delete(f"/api/festivals/{festival_id}/")

        assert response.status_code == status.HTTP_404_NOT_FOUND, (
            "User should get 404 when trying to delete another user's festival"
        )

        # Verify the festival still exists
        assert Festival.objects.filter(id=festival_id).exists(), (
            "Festival should not have been deleted"
        )


# ============================================================================
# ADMIN USER ACCESS CONTROL TESTS
# ============================================================================


@pytest.mark.django_db
class TestAdminAccessControl:
    """
    Test suite for admin staff user visibility.

    Admin users should see:
    - Their own organisations (both seeded and created)
    - All user-created organisations from other users (is_seed_clone=False, user!=None)

    Admin users should NOT see:
    - Other users' seed-cloned organisations (privacy protection)
    - Seed template organisations (user=None)
    """

    def test_admin_sees_own_and_user_created_festivals(
        self,
        api_client,
        admin_user,
        admin_seeded_festival,
        admin_created_festival,
        user1_seeded_festival,
        user1_created_festival,
        user2_seeded_festival,
        user2_created_festival,
        seed_template_festival,
    ):
        """
        Admin sees all seed templates + all user-created organisations.

        Admin should see:
        - seed_template_festival (template with user=NULL - admins manage seeds)
        - admin_seeded_festival (their own, seeded)
        - admin_created_festival (their own, created)
        - user1_created_festival (other user's created)
        - user2_created_festival (other user's created)

        Admin should NOT see:
        - user1_seeded_festival (other user's seeded clone - their private copy)
        - user2_seeded_festival (other user's seeded clone - their private copy)
        """
        api_client.force_authenticate(user=admin_user)
        response = api_client.get("/api/festivals/")

        assert response.status_code == status.HTTP_200_OK
        print(response.data)
        assert response.data["count"] == 5

        festival_names = {festival["name"] for festival in response.data["results"]}

        # Admin should see their own festivals (both seeded and created)
        assert "Admin Seeded Festival" in festival_names, (
            "Admin should see their own seeded festival"
        )
        assert "Admin Created Festival" in festival_names, (
            "Admin should see their own created festival"
        )

        # Admin should see user-created festivals from other users
        assert "User1 Created Festival" in festival_names, (
            "Admin should see user-created festivals from other users"
        )
        assert "User2 Created Festival" in festival_names, (
            "Admin should see user-created festivals from other users"
        )

        # Admin should NOT see other users' seeded festivals (privacy)
        assert "User1 Seeded Festival" not in festival_names, (
            "Admin should NOT see other users' seeded festivals (privacy protection)"
        )
        assert "User2 Seeded Festival" not in festival_names, (
            "Admin should NOT see other users' seeded festivals (privacy protection)"
        )

        # Admin SHOULD see template festivals (to manage them)
        assert "Seed Template Festival" in festival_names, (
            "Admin should see template festivals (user=NULL) to manage seeds"
        )

    def test_admin_can_access_user_created_festival_by_id(
        self,
        api_client,
        admin_user,
        user1_created_festival,
    ):
        """
        Admin can access user-created festivals by ID.

        Admin should be able to retrieve details of user-created festivals
        from other users (useful for support/debugging).
        """
        api_client.force_authenticate(user=admin_user)
        response = api_client.get(f"/api/festivals/{user1_created_festival.id}/")

        assert response.status_code == status.HTTP_200_OK, (
            "Admin should be able to access user-created festivals by ID"
        )
        assert response.data["name"] == "User1 Created Festival"
        assert response.data["country"] == "Spain"

    def test_admin_cannot_access_user_seeded_festival_by_id(
        self,
        api_client,
        admin_user,
        user1_seeded_festival,
    ):
        """
        Admin cannot access other users' seeded clones by ID.

        Seeded clones (is_seed_clone=True, user=other_user) are private copies
        of seed templates given to users on registration. Admins should NOT
        access other users' private copies (privacy protection).
        Admins CAN see and manage the seed templates (user=NULL) directly.
        """
        api_client.force_authenticate(user=admin_user)
        response = api_client.get(f"/api/festivals/{user1_seeded_festival.id}/")

        assert response.status_code == status.HTTP_404_NOT_FOUND, (
            "Admin should get 404 when trying to access other users' seeded festivals"
        )

    def test_admin_can_modify_user_created_festival(
        self,
        api_client,
        admin_user,
        user1_created_festival,
    ):
        """
        Admin can modify user-created festivals from other users.

        This is useful for admin support scenarios where they need to
        help users fix issues with their data.
        """
        api_client.force_authenticate(user=admin_user)
        response = api_client.patch(
            f"/api/festivals/{user1_created_festival.id}/",
            {"description": "Updated by admin"},
        )

        assert response.status_code == status.HTTP_200_OK, (
            "Admin should be able to modify user-created festivals"
        )

        user1_created_festival.refresh_from_db()
        assert user1_created_festival.description == "Updated by admin", (
            "Festival should have been updated by admin"
        )

    def test_admin_cannot_modify_user_seeded_festival(
        self,
        api_client,
        admin_user,
        user1_seeded_festival,
    ):
        """
        Admin cannot modify other users' seeded festivals.

        Seeded festivals are protected from admin access to maintain
        privacy and prevent accidental modifications.
        """
        api_client.force_authenticate(user=admin_user)
        response = api_client.patch(
            f"/api/festivals/{user1_seeded_festival.id}/",
            {"description": "Attempted admin update"},
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND, (
            "Admin should get 404 when trying to modify other users' seeded festivals"
        )

        user1_seeded_festival.refresh_from_db()
        assert user1_seeded_festival.description == "Cloned during registration", (
            "Seeded festival should not have been modified"
        )


# ============================================================================
# IS_SEED_CLONE FLAG TESTS
# ============================================================================


@pytest.mark.django_db
class TestIsSeedCloneFlag:
    """
    Test suite for verifying correct setting of is_seed_clone flag.

    The is_seed_clone flag is critical for the access control system.
    It must be:
    - False when users create organisations via API
    - True when organisations are cloned during registration
    """

    def test_api_created_festival_has_seed_clone_false(self, api_client, user1):
        """
        Festival created via API should have is_seed_clone=False.

        When users create organisations through the API, these are
        considered user-created content and should be visible to admins.
        """
        api_client.force_authenticate(user=user1)
        response = api_client.post(
            "/api/festivals/",
            {
                "name": "API Created Festival",
                "country": "Portugal",
                "town": "Lisbon",
                "festival_type": "MUSIC",
            },
        )

        assert response.status_code == status.HTTP_201_CREATED

        festival = Festival.objects.get(id=response.data["id"])
        assert festival.is_seed_clone is False, (
            "API-created festival should have is_seed_clone=False"
        )
        assert festival.user == user1, (
            "API-created festival should be assigned to the requesting user"
        )

    def test_registration_signal_sets_seed_clone_true(self, db):
        """
        Festivals cloned during registration should have is_seed_clone=True.

        This test verifies that the registration signal (seed_user_organisations)
        correctly sets is_seed_clone=True when cloning template organisations
        for new users.

        Note: This test creates a seed template and triggers user creation
        to verify the signal behavior.
        """
        # Create a seed template festival (user=NULL)
        Festival.objects.create(
            name="Registration Seed Template",
            description="Will be cloned",
            country="Belgium",
            town="Brussels",
            festival_type="CIRCUS",
            user=None,
            is_seed_clone=False,  # Templates themselves are not clones
        )

        # Create a new user (this should trigger the registration signal)
        new_user = Profile.objects.create_user(
            email="newuser@example.com",
            password="testpass123",
            first_name="New",
            last_name="User",
        )

        # Verify the festival was cloned with is_seed_clone=True
        cloned_festivals = Festival.objects.filter(user=new_user, name="Registration Seed Template")

        assert cloned_festivals.exists(), "Seed template should have been cloned for new user"

        cloned_festival = cloned_festivals.first()
        assert cloned_festival.is_seed_clone is True, (
            "Cloned festival should have is_seed_clone=True"
        )
        assert cloned_festival.user == new_user, (
            "Cloned festival should be assigned to the new user"
        )

    def test_seed_clone_flag_persists_on_update(self, api_client, user1, user1_seeded_festival):
        """
        The is_seed_clone flag should persist when festival is updated.

        When users edit their seeded festivals, the is_seed_clone flag
        should remain True. This ensures the visibility rules continue
        to work correctly.
        """
        api_client.force_authenticate(user=user1)
        response = api_client.patch(
            f"/api/festivals/{user1_seeded_festival.id}/",
            {"description": "Updated description"},
        )

        assert response.status_code == status.HTTP_200_OK

        user1_seeded_festival.refresh_from_db()
        assert user1_seeded_festival.is_seed_clone is True, (
            "is_seed_clone should remain True after update"
        )
        assert user1_seeded_festival.description == "Updated description", (
            "Description should have been updated"
        )

    def test_user_created_flag_persists_on_update(self, api_client, user1, user1_created_festival):
        """
        The is_seed_clone=False flag should persist when festival is updated.

        When users edit their user-created festivals, the is_seed_clone flag
        should remain False.
        """
        api_client.force_authenticate(user=user1)
        response = api_client.patch(
            f"/api/festivals/{user1_created_festival.id}/",
            {"description": "Updated description"},
        )

        assert response.status_code == status.HTTP_200_OK

        user1_created_festival.refresh_from_db()
        assert user1_created_festival.is_seed_clone is False, (
            "is_seed_clone should remain False after update"
        )
        assert user1_created_festival.description == "Updated description", (
            "Description should have been updated"
        )


# ============================================================================
# INCLUDE_DELETED PARAMETER TESTS
# ============================================================================


@pytest.mark.django_db
class TestIncludeDeletedWithAccessControl:
    """
    Test suite for include_deleted parameter with access control.

    The access control rules should apply consistently whether or not
    deleted organisations are included in the results.
    """

    def test_regular_user_include_deleted_respects_access_control(
        self,
        api_client,
        user1,
        user1_created_festival,
        user2_created_festival,
    ):
        """
        Regular user with include_deleted=true should still only see own festivals.

        The include_deleted parameter should not bypass access control.
        User1 should see their deleted festivals but not user2's deleted festivals.
        """
        # Soft delete both festivals
        user1_created_festival.delete()
        user2_created_festival.delete()

        api_client.force_authenticate(user=user1)
        response = api_client.get("/api/festivals/?include_deleted=true")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 1, "User should see only their own deleted festival"

        assert response.data["results"][0]["name"] == "User1 Created Festival", (
            "User should see their deleted festival"
        )

    def test_admin_include_deleted_respects_access_control(
        self,
        api_client,
        admin_user,
        admin_created_festival,
        user1_seeded_festival,
        user1_created_festival,
    ):
        """
        Admin with include_deleted=true should see own + user-created deleted festivals.

        Admin should see:
        - Their own deleted festivals
        - User-created deleted festivals from other users

        Admin should NOT see:
        - Other users' deleted seeded festivals
        """
        # Soft delete all festivals
        admin_created_festival.delete()
        user1_seeded_festival.delete()
        user1_created_festival.delete()

        api_client.force_authenticate(user=admin_user)
        response = api_client.get("/api/festivals/?include_deleted=true")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 2, (
            "Admin should see 2 deleted festivals (own + user1's created)"
        )

        festival_names = {festival["name"] for festival in response.data["results"]}
        assert "Admin Created Festival" in festival_names, (
            "Admin should see their own deleted festival"
        )
        assert "User1 Created Festival" in festival_names, (
            "Admin should see user-created deleted festival"
        )
        assert "User1 Seeded Festival" not in festival_names, (
            "Admin should NOT see other users' deleted seeded festivals"
        )


# ============================================================================
# EDGE CASES AND BOUNDARY TESTS
# ============================================================================


@pytest.mark.django_db
class TestAccessControlEdgeCases:
    """
    Test suite for edge cases and boundary conditions.

    These tests verify correct behavior in unusual scenarios.
    """

    def test_unauthenticated_user_gets_401(self, api_client):
        """
        Unauthenticated requests should be rejected.

        Users must be authenticated to access the festivals endpoint.
        """
        response = api_client.get("/api/festivals/")
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_empty_list_for_new_user_with_no_festivals(self, api_client, db):
        """
        New user with no festivals should see empty list.

        If a user has not been seeded and has not created any festivals,
        they should see an empty list (not an error).
        """
        # Create a user but bypass the registration signal
        # (simulating a user created directly in tests)
        user = Profile.objects.create_user(
            email="emptyuser@example.com",
            password="testpass123",
        )

        # Manually clear any seed-cloned festivals that might have been created
        Festival.objects.filter(user=user).delete()

        api_client.force_authenticate(user=user)
        response = api_client.get("/api/festivals/")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 0, "User with no festivals should see empty list"

    def test_admin_flag_change_affects_visibility(
        self,
        api_client,
        user1,
        user1_created_festival,
        user2_created_festival,
    ):
        """
        Changing user's is_staff flag should change their visibility.

        When a user is promoted to admin, they should immediately see
        user-created festivals from other users.
        """
        # Initially user1 is not staff - should see only own festival
        api_client.force_authenticate(user=user1)
        response = api_client.get("/api/festivals/")
        assert response.data["count"] == 1

        # Promote user1 to admin
        user1.is_staff = True
        user1.save()

        # Now user1 should see user-created festivals from others
        response = api_client.get("/api/festivals/")
        assert response.data["count"] == 2, (
            "After promotion to admin, user should see user-created festivals from others"
        )

        festival_names = {festival["name"] for festival in response.data["results"]}
        assert "User1 Created Festival" in festival_names
        assert "User2 Created Festival" in festival_names

    def test_queryset_distinct_prevents_duplicates(
        self,
        api_client,
        admin_user,
        user1_created_festival,
    ):
        """
        Verify that .distinct() prevents duplicate results.

        The visibility filter uses Q objects with OR conditions,
        which could theoretically produce duplicates. The .distinct()
        call should prevent this.
        """
        api_client.force_authenticate(user=admin_user)
        response = api_client.get("/api/festivals/")

        # Count how many times each festival ID appears
        festival_ids = [festival["id"] for festival in response.data["results"]]
        unique_ids = set(festival_ids)

        assert len(festival_ids) == len(unique_ids), (
            "No duplicate festivals should appear in results"
        )

    def test_seed_template_visibility(
        self,
        api_client,
        admin_user,
        user1,
        seed_template_festival,
    ):
        """
        Seed templates (user=NULL) should be visible to admins but not regular users.

        Seed templates are managed by admins and used during user registration.
        - Admins see seeds to manage them
        - Regular users do not see the template (they get clones of it)
        """
        # Check admin - SHOULD see seed template
        api_client.force_authenticate(user=admin_user)
        response = api_client.get("/api/festivals/")
        festival_names = {festival["name"] for festival in response.data["results"]}
        assert "Seed Template Festival" in festival_names, (
            "Admin should see seed templates to manage them"
        )

        # Check regular user - should NOT see seed template
        api_client.force_authenticate(user=user1)
        response = api_client.get("/api/festivals/")
        festival_names = {festival["name"] for festival in response.data["results"]}
        assert "Seed Template Festival" not in festival_names, (
            "Regular user should not see seed templates (they get cloned copies instead)"
        )

    def test_multiple_admins_see_same_user_created_content(
        self,
        api_client,
        db,
        user1_created_festival,
    ):
        """
        Multiple admins should all see the same user-created content.

        If there are multiple admin users, they should all see the same
        set of user-created organisations from regular users.
        """
        admin1 = Profile.objects.create_user(
            email="admin1@example.com",
            password="testpass123",
            is_staff=True,
        )
        admin2 = Profile.objects.create_user(
            email="admin2@example.com",
            password="testpass123",
            is_staff=True,
        )

        # Both admins should see user1's created festival
        api_client.force_authenticate(user=admin1)
        response1 = api_client.get("/api/festivals/")
        names1 = {festival["name"] for festival in response1.data["results"]}

        api_client.force_authenticate(user=admin2)
        response2 = api_client.get("/api/festivals/")
        names2 = {festival["name"] for festival in response2.data["results"]}

        assert "User1 Created Festival" in names1, "Admin1 should see user-created festival"
        assert "User1 Created Festival" in names2, "Admin2 should see user-created festival"

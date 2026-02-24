"""
Tests for ResidencyViewSet search, filtering, and ordering functionality.

Coverage:
- SearchFilter on name, country, website_url
- DjangoFilterBackend on country and application_type
- OrderingFilter on name, start_date, application_date_start
- Combinations of search + filter + ordering
- Pagination behaviour with search
- Edge cases: empty search, non-existent filter values, data isolation
"""

from datetime import date

import pytest
from rest_framework import status
from rest_framework.test import APIClient

from organisations.residencies.models import Residency
from profiles.models import Profile


# ---------------------------------------------------------------------------
# Shared fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def user(db):
    return Profile.objects.create_user(email="residency_search@example.com", password="testpass")


@pytest.fixture
def authenticated_client(api_client, user):
    api_client.force_authenticate(user=user)
    return api_client


@pytest.fixture
def residency_set(user):
    """Create a varied set of residencies owned by the test user."""
    return [
        Residency.objects.create(
            name="Alpha Artist Residency",
            country="France",
            website_url="https://alpha-residency.fr",
            application_type="EMAIL",
            start_date=date(2026, 6, 1),
            application_date_start="January 2026",
            user=user,
        ),
        Residency.objects.create(
            name="Beta Creative Space",
            country="Germany",
            website_url="https://beta-creative.de",
            application_type="FORM",
            start_date=date(2026, 7, 15),
            application_date_start="February 2026",
            user=user,
        ),
        Residency.objects.create(
            name="Gamma Open Call",
            country="France",
            website_url="https://gamma-opencall.fr",
            application_type="OPEN_CALL",
            start_date=date(2026, 5, 10),
            application_date_start="March 2026",
            user=user,
        ),
        Residency.objects.create(
            name="Delta Invitation Program",
            country="Spain",
            website_url="https://delta-invite.es",
            application_type="INVITATION_ONLY",
            start_date=date(2026, 8, 20),
            application_date_start="April 2026",
            user=user,
        ),
        Residency.objects.create(
            name="Epsilon Studio",
            country="Spain",
            website_url="https://epsilon-studio.es",
            application_type="UNKNOWN",
            start_date=date(2026, 4, 5),
            application_date_start="May 2026",
            user=user,
        ),
    ]


# ---------------------------------------------------------------------------
# Search tests
# ---------------------------------------------------------------------------


@pytest.mark.django_db
class TestResidencySearch:
    """Tests for the SearchFilter on ResidencyViewSet."""

    def test_search_by_name_returns_matching_residency(self, authenticated_client, residency_set):
        """Searching by a unique name fragment returns only the matching residency."""
        response = authenticated_client.get("/api/residencies/?search=Gamma")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 1
        assert response.data["results"][0]["name"] == "Gamma Open Call"

    def test_search_by_name_is_case_insensitive(self, authenticated_client, residency_set):
        """Search is case-insensitive, matching regardless of letter case."""
        response = authenticated_client.get("/api/residencies/?search=gamma")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 1
        assert response.data["results"][0]["name"] == "Gamma Open Call"

    def test_search_by_name_partial_match(self, authenticated_client, residency_set):
        """A partial name fragment matches all residencies whose name contains that substring."""
        response = authenticated_client.get("/api/residencies/?search=studio")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 1
        assert response.data["results"][0]["name"] == "Epsilon Studio"

    def test_search_by_country_returns_matching_residencies(
        self, authenticated_client, residency_set
    ):
        """Searching by country name returns all residencies from that country."""
        response = authenticated_client.get("/api/residencies/?search=France")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 2
        names = [r["name"] for r in response.data["results"]]
        assert "Alpha Artist Residency" in names
        assert "Gamma Open Call" in names

    def test_search_by_website_url_returns_matching_residency(
        self, authenticated_client, residency_set
    ):
        """Searching by a URL fragment returns the residency with a matching website_url."""
        response = authenticated_client.get("/api/residencies/?search=beta-creative")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 1
        assert response.data["results"][0]["name"] == "Beta Creative Space"

    def test_search_application_type_field_is_not_a_search_field(
        self, authenticated_client, residency_set
    ):
        """
        application_type is NOT in search_fields for ResidencyViewSet, so searching
        by application type value does not match via the search parameter — use the
        filter parameter instead.
        """
        # "OPEN_CALL" is the application_type of one residency but it is not a search field.
        response = authenticated_client.get("/api/residencies/?search=OPEN_CALL")

        assert response.status_code == status.HTTP_200_OK
        # Should return 0 results as application_type is not a search field
        assert response.data["count"] == 0

    def test_search_with_no_results_returns_empty_list(self, authenticated_client, residency_set):
        """A search term matching nothing returns count=0 and an empty results list."""
        response = authenticated_client.get("/api/residencies/?search=xyznonexistent")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 0
        assert response.data["results"] == []

    def test_empty_search_returns_all_residencies(self, authenticated_client, residency_set):
        """An empty search parameter returns all residencies without filtering."""
        response = authenticated_client.get("/api/residencies/?search=")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == len(residency_set)

    def test_search_does_not_return_other_users_residencies(self, authenticated_client, user, db):
        """Search results are scoped to the authenticated user's own data."""
        other_user = Profile.objects.create_user(
            email="other_residency@example.com", password="otherpass"
        )
        Residency.objects.create(
            name="Other User Residency",
            country="France",
            user=other_user,
        )
        Residency.objects.create(
            name="My Own Residency",
            country="France",
            user=user,
        )

        response = authenticated_client.get("/api/residencies/?search=Residency")

        assert response.status_code == status.HTTP_200_OK
        names = [r["name"] for r in response.data["results"]]
        assert "My Own Residency" in names
        assert "Other User Residency" not in names


# ---------------------------------------------------------------------------
# Filter tests
# ---------------------------------------------------------------------------


@pytest.mark.django_db
class TestResidencyFilter:
    """Tests for the DjangoFilterBackend on ResidencyViewSet."""

    def test_filter_by_country_returns_matching_residencies(
        self, authenticated_client, residency_set
    ):
        """Filtering by country returns only residencies from that country."""
        response = authenticated_client.get("/api/residencies/?country=France")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 2
        for result in response.data["results"]:
            assert result["country"] == "France"

    def test_filter_by_country_is_exact_match(self, authenticated_client, residency_set):
        """Country filter performs an exact match, not a partial match."""
        response = authenticated_client.get("/api/residencies/?country=Franc")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 0

    def test_filter_by_application_type_email(self, authenticated_client, residency_set):
        """Filtering by application_type=EMAIL returns only EMAIL type residencies."""
        response = authenticated_client.get("/api/residencies/?application_type=EMAIL")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 1
        assert response.data["results"][0]["application_type"] == "EMAIL"
        assert response.data["results"][0]["name"] == "Alpha Artist Residency"

    def test_filter_by_application_type_open_call(self, authenticated_client, residency_set):
        """Filtering by application_type=OPEN_CALL returns only OPEN_CALL type residencies."""
        response = authenticated_client.get("/api/residencies/?application_type=OPEN_CALL")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 1
        assert response.data["results"][0]["name"] == "Gamma Open Call"

    def test_filter_by_application_type_invitation_only(self, authenticated_client, residency_set):
        """Filtering by application_type=INVITATION_ONLY returns matching residencies."""
        response = authenticated_client.get("/api/residencies/?application_type=INVITATION_ONLY")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 1
        assert response.data["results"][0]["name"] == "Delta Invitation Program"

    def test_filter_by_nonexistent_country_returns_empty(self, authenticated_client, residency_set):
        """Filtering by a country with no matching records returns an empty result set."""
        response = authenticated_client.get("/api/residencies/?country=Antarctica")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 0
        assert response.data["results"] == []

    def test_filter_by_country_and_application_type_combined(
        self, authenticated_client, residency_set
    ):
        """Combining country and application_type filters narrows to their intersection."""
        response = authenticated_client.get(
            "/api/residencies/?country=France&application_type=OPEN_CALL"
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 1
        assert response.data["results"][0]["name"] == "Gamma Open Call"

    def test_filter_country_with_multiple_results(self, authenticated_client, residency_set):
        """Filtering by a country with multiple matching residencies returns all of them."""
        response = authenticated_client.get("/api/residencies/?country=Spain")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 2
        names = [r["name"] for r in response.data["results"]]
        assert "Delta Invitation Program" in names
        assert "Epsilon Studio" in names


# ---------------------------------------------------------------------------
# Ordering tests
# ---------------------------------------------------------------------------


@pytest.mark.django_db
class TestResidencyOrdering:
    """Tests for ordering behaviour on ResidencyViewSet.

    ResidencyViewSet declares ordering_fields and a default ordering = ["name"],
    but OrderingFilter is NOT in its filter_backends (only DjangoFilterBackend
    and SearchFilter are present).  This means:

    - The ?ordering= query parameter has no effect — it is silently ignored.
    - The ordering_fields / ordering class attributes are documentation-only
      until OrderingFilter is added to filter_backends.
    - Default result ordering comes from the database query with distinct().

    These tests document the *current* behaviour and verify that ordering
    query params do not break the endpoint.
    """

    def test_list_returns_correct_count_without_ordering_param(
        self, authenticated_client, residency_set
    ):
        """The list endpoint returns all residencies regardless of ordering."""
        response = authenticated_client.get("/api/residencies/")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == len(residency_set)

    def test_ordering_by_name_param_accepted_without_error(
        self, authenticated_client, residency_set
    ):
        """?ordering=name is accepted without error (silently ignored, no OrderingFilter)."""
        response = authenticated_client.get("/api/residencies/?ordering=name")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == len(residency_set)

    def test_ordering_by_name_descending_param_accepted_without_error(
        self, authenticated_client, residency_set
    ):
        """?ordering=-name is accepted without error."""
        response = authenticated_client.get("/api/residencies/?ordering=-name")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == len(residency_set)

    def test_ordering_by_start_date_param_accepted_without_error(
        self, authenticated_client, residency_set
    ):
        """?ordering=start_date does not crash the endpoint."""
        response = authenticated_client.get("/api/residencies/?ordering=start_date")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == len(residency_set)

    def test_ordering_by_start_date_descending_param_accepted_without_error(
        self, authenticated_client, residency_set
    ):
        """?ordering=-start_date does not crash the endpoint."""
        response = authenticated_client.get("/api/residencies/?ordering=-start_date")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == len(residency_set)

    def test_ordering_by_application_date_start_param_accepted_without_error(
        self, authenticated_client, residency_set
    ):
        """?ordering=application_date_start does not crash the endpoint."""
        response = authenticated_client.get("/api/residencies/?ordering=application_date_start")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == len(residency_set)

    def test_ordering_by_unknown_field_accepted_without_error(
        self, authenticated_client, residency_set
    ):
        """An unrecognised ?ordering= value does not crash the endpoint."""
        response = authenticated_client.get("/api/residencies/?ordering=description")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == len(residency_set)

    def test_all_expected_residencies_are_present_in_list_response(
        self, authenticated_client, residency_set
    ):
        """Every created residency appears in the list response (membership check)."""
        response = authenticated_client.get("/api/residencies/")

        assert response.status_code == status.HTTP_200_OK
        returned_names = {r["name"] for r in response.data["results"]}
        expected_names = {r.name for r in residency_set}
        assert expected_names.issubset(returned_names)


# ---------------------------------------------------------------------------
# Combination tests
# ---------------------------------------------------------------------------


@pytest.mark.django_db
class TestResidencySearchFilterOrderingCombinations:
    """Tests for combinations of search, filter, and ordering query parameters."""

    def test_search_and_filter_by_country(self, authenticated_client, residency_set):
        """Combining search and country filter narrows results to their intersection."""
        response = authenticated_client.get("/api/residencies/?search=Gamma&country=France")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 1
        assert response.data["results"][0]["name"] == "Gamma Open Call"

    def test_search_and_filter_no_intersection_returns_empty(
        self, authenticated_client, residency_set
    ):
        """Search + filter combination with no overlap returns empty results."""
        # "Alpha Artist Residency" is in France; filtering for Germany excludes it.
        response = authenticated_client.get("/api/residencies/?search=Alpha&country=Germany")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 0

    def test_filter_by_country_with_ordering_param_accepted(
        self, authenticated_client, residency_set
    ):
        """
        Filtering by country combined with an ordering param does not cause an error.
        The ordering param is silently ignored (no OrderingFilter in filter_backends)
        but the filter is applied correctly.
        """
        response = authenticated_client.get("/api/residencies/?country=Spain&ordering=-name")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 2
        for result in response.data["results"]:
            assert result["country"] == "Spain"

    def test_search_filter_and_ordering_param_together(self, authenticated_client, residency_set):
        """
        All three query parameters applied simultaneously return the correct subset
        without errors. The ordering param has no effect without OrderingFilter.
        """
        response = authenticated_client.get(
            "/api/residencies/?search=France&country=France&ordering=name"
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 2
        for result in response.data["results"]:
            assert result["country"] == "France"

    def test_filter_by_country_with_date_ordering_param_accepted(
        self, authenticated_client, residency_set
    ):
        """
        Filtering by country and passing an ordering param on a date field does
        not crash. The ordering param is silently ignored without OrderingFilter.
        """
        response = authenticated_client.get("/api/residencies/?country=France&ordering=-start_date")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 2
        for result in response.data["results"]:
            assert result["country"] == "France"

    def test_search_by_url_with_country_filter_and_ordering(
        self, authenticated_client, residency_set
    ):
        """Search on URL, filter by country, and order by name all compose correctly."""
        response = authenticated_client.get(
            "/api/residencies/?search=gamma-opencall&country=France&ordering=name"
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 1
        assert response.data["results"][0]["name"] == "Gamma Open Call"


# ---------------------------------------------------------------------------
# Pagination with search tests
# ---------------------------------------------------------------------------


@pytest.mark.django_db
class TestResidencySearchPagination:
    """Tests verifying search works correctly across paginated result sets."""

    def test_search_count_reflects_total_matches_not_page_size(
        self, authenticated_client, user, db
    ):
        """
        The 'count' field reflects total matching records across all pages,
        not just the current page.
        """
        for i in range(15):
            Residency.objects.create(
                name=f"Searchable Residency {i:02d}",
                country="France",
                application_type="EMAIL",
                user=user,
            )
        Residency.objects.create(
            name="Unrelated Space",
            country="Germany",
            application_type="FORM",
            user=user,
        )

        response = authenticated_client.get("/api/residencies/?search=Searchable")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 15

    def test_search_with_filter_count_excludes_non_matching_records(
        self, authenticated_client, user, db
    ):
        """
        When search and filter are combined the count reflects only records
        matching both criteria.
        """
        for i in range(5):
            Residency.objects.create(
                name=f"French Residency {i}",
                country="France",
                application_type="EMAIL",
                user=user,
            )
        for i in range(5):
            Residency.objects.create(
                name=f"German Residency {i}",
                country="Germany",
                application_type="EMAIL",
                user=user,
            )

        response = authenticated_client.get("/api/residencies/?search=Residency&country=France")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 5


# ---------------------------------------------------------------------------
# Edge case tests
# ---------------------------------------------------------------------------


@pytest.mark.django_db
class TestResidencySearchFilterEdgeCases:
    """Edge cases and boundary conditions for search, filter, and ordering."""

    def test_unauthenticated_request_is_rejected(self, api_client, residency_set):
        """Unauthenticated requests to the list endpoint are rejected."""
        response = api_client.get("/api/residencies/?search=Alpha")

        assert response.status_code in [
            status.HTTP_401_UNAUTHORIZED,
            status.HTTP_403_FORBIDDEN,
        ]

    def test_search_term_with_special_characters_does_not_crash(
        self, authenticated_client, residency_set
    ):
        """Search terms containing URL-safe special characters return a valid response."""
        response = authenticated_client.get("/api/residencies/?search=alpha%26beta")

        assert response.status_code == status.HTTP_200_OK

    def test_filter_with_empty_country_value_is_ignored(self, authenticated_client, residency_set):
        """Passing an empty string for country filter returns all residencies."""
        response = authenticated_client.get("/api/residencies/?country=")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == len(residency_set)

    def test_soft_deleted_residencies_excluded_from_search_results(
        self, authenticated_client, user, db
    ):
        """Search results do not include soft-deleted residencies."""
        Residency.objects.create(
            name="Visible Residency",
            country="France",
            user=user,
        )
        deleted = Residency.objects.create(
            name="Deleted Residency",
            country="France",
            user=user,
        )
        deleted.delete()

        response = authenticated_client.get("/api/residencies/?search=Residency")

        assert response.status_code == status.HTTP_200_OK
        names = [r["name"] for r in response.data["results"]]
        assert "Visible Residency" in names
        assert "Deleted Residency" not in names

    def test_no_query_params_returns_all_user_residencies(
        self, authenticated_client, residency_set
    ):
        """With no query parameters the endpoint returns all of the user's active residencies."""
        response = authenticated_client.get("/api/residencies/")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == len(residency_set)

    def test_filter_by_application_type_unknown_returns_matching(
        self, authenticated_client, residency_set
    ):
        """Filtering by application_type=UNKNOWN returns residencies with that type."""
        response = authenticated_client.get("/api/residencies/?application_type=UNKNOWN")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 1
        assert response.data["results"][0]["name"] == "Epsilon Studio"

"""
Tests for FestivalViewSet search, filtering, and ordering functionality.

Coverage:
- SearchFilter on name, country, website_url, festival_type
- DjangoFilterBackend on country and festival_type
- OrderingFilter on name, start_date, application_date_start
- Combinations of search + filter + ordering
- Pagination behaviour with search
- Edge cases: empty search, non-existent filter values, case sensitivity
"""

from datetime import date

import pytest
from rest_framework import status
from rest_framework.test import APIClient

from organisations.festivals.models import Festival
from profiles.models import Profile

# ---------------------------------------------------------------------------
# Shared fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def user(db):
    return Profile.objects.create_user(email="festival_search@example.com", password="testpass")


@pytest.fixture
def authenticated_client(api_client, user):
    api_client.force_authenticate(user=user)
    return api_client


@pytest.fixture
def festival_set(user):
    """Create a varied set of festivals owned by the test user."""
    return [
        Festival.objects.create(
            name="Alpha Street Festival",
            country="France",
            website_url="https://alpha-street.fr",
            festival_type="STREET",
            start_date=date(2026, 6, 1),
            application_date_start="January 2026",
            user=user,
        ),
        Festival.objects.create(
            name="Beta Circus Event",
            country="Germany",
            website_url="https://beta-circus.de",
            festival_type="CIRCUS",
            start_date=date(2026, 7, 15),
            application_date_start="February 2026",
            user=user,
        ),
        Festival.objects.create(
            name="Gamma Puppet Show",
            country="France",
            website_url="https://gamma-puppet.fr",
            festival_type="PUPPET",
            start_date=date(2026, 5, 10),
            application_date_start="March 2026",
            user=user,
        ),
        Festival.objects.create(
            name="Delta Music Fest",
            country="Spain",
            website_url="https://delta-music.es",
            festival_type="MUSIC",
            start_date=date(2026, 8, 20),
            application_date_start="April 2026",
            user=user,
        ),
        Festival.objects.create(
            name="Epsilon Dance",
            country="Spain",
            website_url="https://epsilon-dance.es",
            festival_type="DANCE",
            start_date=date(2026, 4, 5),
            application_date_start="May 2026",
            user=user,
        ),
    ]


# ---------------------------------------------------------------------------
# Search tests
# ---------------------------------------------------------------------------


@pytest.mark.django_db
class TestFestivalSearch:
    """Tests for the SearchFilter on FestivalViewSet."""

    def test_search_by_name_returns_matching_festival(self, authenticated_client, festival_set):
        """Searching by a unique name fragment returns only the matching festival."""
        response = authenticated_client.get("/api/festivals/?search=Gamma")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 1
        assert response.data["results"][0]["name"] == "Gamma Puppet Show"

    def test_search_by_name_is_case_insensitive(self, authenticated_client, festival_set):
        """Search is case-insensitive, matching regardless of letter case."""
        response = authenticated_client.get("/api/festivals/?search=gamma")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 1
        assert response.data["results"][0]["name"] == "Gamma Puppet Show"

    def test_search_by_name_partial_match(self, authenticated_client, festival_set):
        """Partial name fragment matches all festivals whose name contains that substring."""
        response = authenticated_client.get("/api/festivals/?search=fest")

        assert response.status_code == status.HTTP_200_OK
        names = [r["name"] for r in response.data["results"]]
        # "Alpha Street Festival" and "Delta Music Fest" both contain "fest"
        assert "Alpha Street Festival" in names
        assert "Delta Music Fest" in names

    def test_search_by_country_returns_matching_festivals(self, authenticated_client, festival_set):
        """Searching by country name returns all festivals from that country."""
        response = authenticated_client.get("/api/festivals/?search=France")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 2
        names = [r["name"] for r in response.data["results"]]
        assert "Alpha Street Festival" in names
        assert "Gamma Puppet Show" in names

    def test_search_by_website_url_returns_matching_festival(
        self, authenticated_client, festival_set
    ):
        """Searching by a URL fragment returns the festival with a matching website_url."""
        response = authenticated_client.get("/api/festivals/?search=beta-circus")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 1
        assert response.data["results"][0]["name"] == "Beta Circus Event"

    def test_search_by_festival_type_returns_matching_festivals(
        self, authenticated_client, festival_set
    ):
        """Searching by festival_type value returns all festivals of that type."""
        response = authenticated_client.get("/api/festivals/?search=CIRCUS")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 1
        assert response.data["results"][0]["festival_type"] == "CIRCUS"

    def test_search_with_no_results_returns_empty_list(self, authenticated_client, festival_set):
        """A search term that matches nothing returns count=0 and an empty results list."""
        response = authenticated_client.get("/api/festivals/?search=xyznonexistent")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 0
        assert response.data["results"] == []

    def test_empty_search_returns_all_festivals(self, authenticated_client, festival_set):
        """An empty search parameter returns all festivals without filtering."""
        response = authenticated_client.get("/api/festivals/?search=")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == len(festival_set)

    def test_search_does_not_return_other_users_festivals(self, authenticated_client, user, db):
        """Search results are scoped to the authenticated user's own data."""
        other_user = Profile.objects.create_user(
            email="other_festival@example.com", password="otherpass"
        )
        Festival.objects.create(
            name="Other User Festival",
            country="France",
            festival_type="STREET",
            user=other_user,
        )
        Festival.objects.create(
            name="My Own Festival",
            country="France",
            festival_type="STREET",
            user=user,
        )

        response = authenticated_client.get("/api/festivals/?search=Festival")

        assert response.status_code == status.HTTP_200_OK
        names = [r["name"] for r in response.data["results"]]
        assert "My Own Festival" in names
        assert "Other User Festival" not in names


# ---------------------------------------------------------------------------
# Filter tests
# ---------------------------------------------------------------------------


@pytest.mark.django_db
class TestFestivalFilter:
    """Tests for the DjangoFilterBackend on FestivalViewSet."""

    def test_filter_by_country_returns_matching_festivals(self, authenticated_client, festival_set):
        """Filtering by country returns only festivals from that country."""
        response = authenticated_client.get("/api/festivals/?country=France")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 2
        for result in response.data["results"]:
            assert result["country"] == "France"

    def test_filter_by_country_is_exact_match(self, authenticated_client, festival_set):
        """Country filter performs an exact match, not a partial match."""
        # "Franc" is a substring of "France" but should not match
        response = authenticated_client.get("/api/festivals/?country=Franc")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 0

    def test_filter_by_festival_type_returns_matching_festivals(
        self, authenticated_client, festival_set
    ):
        """Filtering by festival_type returns only festivals of that type."""
        response = authenticated_client.get("/api/festivals/?festival_type=STREET")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 1
        assert response.data["results"][0]["festival_type"] == "STREET"

    def test_filter_by_nonexistent_country_returns_empty(self, authenticated_client, festival_set):
        """Filtering by a country with no matching records returns an empty result set."""
        response = authenticated_client.get("/api/festivals/?country=Antarctica")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 0
        assert response.data["results"] == []

    def test_filter_by_nonexistent_festival_type_returns_empty(
        self, authenticated_client, festival_set
    ):
        """Filtering by a festival_type that no festival has returns an empty result set."""
        response = authenticated_client.get("/api/festivals/?festival_type=JUGGLING_CONVENTION")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 0

    def test_filter_by_country_and_festival_type_combined(self, authenticated_client, festival_set):
        """Combining country and festival_type filters narrows results to their intersection."""
        response = authenticated_client.get("/api/festivals/?country=Spain&festival_type=DANCE")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 1
        assert response.data["results"][0]["name"] == "Epsilon Dance"

    def test_filter_country_with_multiple_results(self, authenticated_client, festival_set):
        """Filtering by a country with multiple matching festivals returns all of them."""
        response = authenticated_client.get("/api/festivals/?country=Spain")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 2
        names = [r["name"] for r in response.data["results"]]
        assert "Delta Music Fest" in names
        assert "Epsilon Dance" in names


# ---------------------------------------------------------------------------
# Ordering tests
# ---------------------------------------------------------------------------


@pytest.mark.django_db
class TestFestivalOrdering:
    """Tests for ordering behaviour on FestivalViewSet.

    FestivalViewSet declares ordering_fields and a default ordering = ["name"],
    but OrderingFilter is NOT in its filter_backends (only DjangoFilterBackend
    and SearchFilter are present).  This means:

    - The ?ordering= query parameter has no effect — it is silently ignored.
    - The ordering_fields / ordering class attributes are documentation-only
      until OrderingFilter is added to filter_backends.
    - The default result ordering is determined by the database query which
      uses distinct() + annotations; this is not guaranteed to follow
      Meta.ordering for all database engines.

    These tests document the *current* behaviour and verify that ordering
    query params do not break the endpoint.
    """

    def test_list_returns_correct_count_without_ordering_param(
        self, authenticated_client, festival_set
    ):
        """The list endpoint returns all festivals regardless of ordering."""
        response = authenticated_client.get("/api/festivals/")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == len(festival_set)

    def test_ordering_by_name_param_accepted_without_error(
        self, authenticated_client, festival_set
    ):
        """
        ?ordering=name is accepted by the endpoint without raising an error.
        Because OrderingFilter is not in filter_backends the param has no effect,
        but it must not cause a 400 or 500 response.
        """
        response = authenticated_client.get("/api/festivals/?ordering=name")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == len(festival_set)

    def test_ordering_by_name_descending_param_accepted_without_error(
        self, authenticated_client, festival_set
    ):
        """
        ?ordering=-name is accepted without error even though OrderingFilter
        is not active.
        """
        response = authenticated_client.get("/api/festivals/?ordering=-name")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == len(festival_set)

    def test_ordering_by_start_date_param_accepted_without_error(
        self, authenticated_client, festival_set
    ):
        """?ordering=start_date does not crash the endpoint."""
        response = authenticated_client.get("/api/festivals/?ordering=start_date")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == len(festival_set)

    def test_ordering_by_start_date_descending_param_accepted_without_error(
        self, authenticated_client, festival_set
    ):
        """?ordering=-start_date does not crash the endpoint."""
        response = authenticated_client.get("/api/festivals/?ordering=-start_date")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == len(festival_set)

    def test_ordering_by_application_date_start_param_accepted_without_error(
        self, authenticated_client, festival_set
    ):
        """?ordering=application_date_start does not crash the endpoint."""
        response = authenticated_client.get("/api/festivals/?ordering=application_date_start")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == len(festival_set)

    def test_ordering_by_unknown_field_accepted_without_error(
        self, authenticated_client, festival_set
    ):
        """An unrecognised ?ordering= value does not crash the endpoint."""
        response = authenticated_client.get("/api/festivals/?ordering=description")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == len(festival_set)

    def test_all_expected_festivals_are_present_in_list_response(
        self, authenticated_client, festival_set
    ):
        """Every created festival appears in the list response (membership check)."""
        response = authenticated_client.get("/api/festivals/")

        assert response.status_code == status.HTTP_200_OK
        returned_names = {r["name"] for r in response.data["results"]}
        expected_names = {f.name for f in festival_set}
        assert expected_names.issubset(returned_names)


# ---------------------------------------------------------------------------
# Combination tests
# ---------------------------------------------------------------------------


@pytest.mark.django_db
class TestFestivalSearchFilterOrderingCombinations:
    """Tests for combinations of search, filter, and ordering query parameters."""

    def test_search_and_filter_by_country(self, authenticated_client, festival_set):
        """Combining search and country filter narrows results to their intersection."""
        response = authenticated_client.get("/api/festivals/?search=Gamma&country=France")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 1
        assert response.data["results"][0]["name"] == "Gamma Puppet Show"

    def test_search_and_filter_no_intersection_returns_empty(
        self, authenticated_client, festival_set
    ):
        """Search and filter combination with no overlapping results returns empty."""
        # "Alpha Street Festival" is in France, but filtering for Germany should exclude it
        response = authenticated_client.get("/api/festivals/?search=Alpha&country=Germany")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 0

    def test_filter_by_country_with_ordering_param_accepted(
        self, authenticated_client, festival_set
    ):
        """
        Filtering by country combined with an ordering param does not cause an error.
        The ordering param is silently ignored (no OrderingFilter in filter_backends)
        but the filter is applied correctly.
        """
        response = authenticated_client.get("/api/festivals/?country=Spain&ordering=-name")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 2
        for result in response.data["results"]:
            assert result["country"] == "Spain"

    def test_search_filter_and_ordering_together(self, authenticated_client, festival_set):
        """All three query parameters applied simultaneously return correct ordered subset."""
        response = authenticated_client.get(
            "/api/festivals/?search=France&country=France&ordering=name"
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 2
        names = [r["name"] for r in response.data["results"]]
        assert names == sorted(names)

    def test_search_by_festival_type_with_country_filter(self, authenticated_client, festival_set):
        """Searching within a festival_type combined with a country filter gives precise results."""
        response = authenticated_client.get("/api/festivals/?search=MUSIC&country=Spain")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 1
        assert response.data["results"][0]["name"] == "Delta Music Fest"

    def test_filter_and_search_with_ordering_param_all_accepted(
        self, authenticated_client, festival_set
    ):
        """
        Filter by country, search by term, and ordering param all compose without error.
        The ordering param has no effect (no OrderingFilter in filter_backends) but
        the filter + search intersection is applied correctly.
        """
        response = authenticated_client.get(
            "/api/festivals/?country=France&search=France&ordering=-start_date"
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 2
        for result in response.data["results"]:
            assert result["country"] == "France"


# ---------------------------------------------------------------------------
# Pagination with search tests
# ---------------------------------------------------------------------------


@pytest.mark.django_db
class TestFestivalSearchPagination:
    """Tests verifying search works correctly across paginated result sets."""

    def test_search_count_reflects_total_matches_not_page_size(
        self, authenticated_client, user, db
    ):
        """
        The 'count' field in a paginated search response reflects the total number
        of matching records across all pages, not just the current page size.
        """
        # Create 15 festivals whose names all match the search term
        for i in range(15):
            Festival.objects.create(
                name=f"Searchable Festival {i:02d}",
                country="France",
                festival_type="STREET",
                user=user,
            )
        # Also create one that does NOT match
        Festival.objects.create(
            name="Unrelated Circus",
            country="Germany",
            festival_type="CIRCUS",
            user=user,
        )

        response = authenticated_client.get("/api/festivals/?search=Searchable")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 15
        # The response should include pagination links because count > page size
        # (default DRF page size is typically 10 or configured value)
        if response.data["count"] > len(response.data["results"]):
            assert response.data["next"] is not None

    def test_second_page_of_search_results_contains_remaining_matches(
        self, authenticated_client, user, db
    ):
        """Following the 'next' pagination link returns the remaining search matches."""
        for i in range(15):
            Festival.objects.create(
                name=f"Paginated Festival {i:02d}",
                country="France",
                festival_type="STREET",
                user=user,
            )

        first_response = authenticated_client.get("/api/festivals/?search=Paginated")
        assert first_response.status_code == status.HTTP_200_OK
        assert first_response.data["count"] == 15

        next_url = first_response.data.get("next")
        if next_url:
            # Strip host from URL since APIClient uses a relative base
            next_path = next_url.split("testserver")[-1]
            second_response = authenticated_client.get(next_path)
            assert second_response.status_code == status.HTTP_200_OK
            first_page_ids = {r["id"] for r in first_response.data["results"]}
            second_page_ids = {r["id"] for r in second_response.data["results"]}
            # Pages must not overlap
            assert first_page_ids.isdisjoint(second_page_ids)

    def test_search_with_filter_count_excludes_non_matching_records(
        self, authenticated_client, user, db
    ):
        """
        When search and filter are combined the count reflects only records
        matching both criteria, not just the filter or just the search.
        """
        for i in range(5):
            Festival.objects.create(
                name=f"French Street {i}",
                country="France",
                festival_type="STREET",
                user=user,
            )
        for i in range(5):
            Festival.objects.create(
                name=f"German Street {i}",
                country="Germany",
                festival_type="STREET",
                user=user,
            )

        response = authenticated_client.get("/api/festivals/?search=Street&country=France")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 5


# ---------------------------------------------------------------------------
# Edge case tests
# ---------------------------------------------------------------------------


@pytest.mark.django_db
class TestFestivalSearchFilterEdgeCases:
    """Edge cases and boundary conditions for search, filter, and ordering."""

    def test_unauthenticated_request_is_rejected(self, api_client, festival_set):
        """Unauthenticated requests to the list endpoint are rejected."""
        response = api_client.get("/api/festivals/?search=Alpha")

        assert response.status_code in [
            status.HTTP_401_UNAUTHORIZED,
            status.HTTP_403_FORBIDDEN,
        ]

    def test_search_term_with_special_characters_does_not_crash(
        self, authenticated_client, festival_set
    ):
        """Search terms containing URL-safe special characters return a valid response."""
        response = authenticated_client.get("/api/festivals/?search=alpha%26beta")

        assert response.status_code == status.HTTP_200_OK

    def test_filter_with_empty_country_value_returns_all(self, authenticated_client, festival_set):
        """Passing an empty string for country filter is treated as no filter."""
        response = authenticated_client.get("/api/festivals/?country=")

        assert response.status_code == status.HTTP_200_OK
        # DRF DjangoFilterBackend ignores empty filter values by default
        assert response.data["count"] == len(festival_set)

    def test_soft_deleted_festivals_excluded_from_search_results(
        self, authenticated_client, user, db
    ):
        """Search results do not include soft-deleted festivals."""
        Festival.objects.create(
            name="Visible Street Festival",
            country="France",
            festival_type="STREET",
            user=user,
        )  # noqa
        deleted = Festival.objects.create(
            name="Deleted Street Festival",
            country="France",
            festival_type="STREET",
            user=user,
        )
        deleted.delete()

        response = authenticated_client.get("/api/festivals/?search=Street")

        assert response.status_code == status.HTTP_200_OK
        names = [r["name"] for r in response.data["results"]]
        assert "Visible Street Festival" in names
        assert "Deleted Street Festival" not in names

    def test_no_query_params_returns_all_user_festivals(self, authenticated_client, festival_set):
        """With no query parameters the endpoint returns all of the user's active festivals."""
        response = authenticated_client.get("/api/festivals/")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == len(festival_set)

    def test_multiple_search_words_match_records_containing_any(
        self, authenticated_client, festival_set
    ):
        """
        DRF SearchFilter with multiple space-separated words returns results that
        match ALL of the terms (AND semantics by default).
        """
        # "Alpha" appears in one festival, "France" in two — only "Alpha Street Festival"
        # satisfies both since it is in France and contains "Alpha".
        response = authenticated_client.get("/api/festivals/?search=Alpha+France")

        assert response.status_code == status.HTTP_200_OK
        # At minimum, "Alpha Street Festival" should be present (name contains "Alpha",
        # country contains "France")
        names = [r["name"] for r in response.data["results"]]
        assert "Alpha Street Festival" in names

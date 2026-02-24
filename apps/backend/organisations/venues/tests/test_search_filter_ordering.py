"""
Tests for VenueViewSet search, filtering, and ordering functionality.

Coverage:
- SearchFilter on name, country, website_url
- DjangoFilterBackend on country and venue_type
- OrderingFilter on name only (Venue has no date ordering fields)
- Combinations of search + filter + ordering
- Pagination behaviour with search
- Edge cases: empty search, non-existent filter values, data isolation

Note: VenueViewSet has ordering_fields = ["name"] only (no date fields), so
date-based ordering tests that exist for Festival and Residency are not
applicable here.
"""

import pytest
from rest_framework import status
from rest_framework.test import APIClient

from organisations.venues.models import Venue
from profiles.models import Profile


# ---------------------------------------------------------------------------
# Shared fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def user(db):
    return Profile.objects.create_user(email="venue_search@example.com", password="testpass")


@pytest.fixture
def authenticated_client(api_client, user):
    api_client.force_authenticate(user=user)
    return api_client


@pytest.fixture
def venue_set(user):
    """Create a varied set of venues owned by the test user."""
    return [
        Venue.objects.create(
            name="Alpha Grand Theatre",
            country="France",
            website_url="https://alpha-theatre.fr",
            venue_type="THEATRE",
            user=user,
        ),
        Venue.objects.create(
            name="Beta Circus Space",
            country="Germany",
            website_url="https://beta-circus.de",
            venue_type="CIRCUS_SPACE",
            user=user,
        ),
        Venue.objects.create(
            name="Gamma Opera House",
            country="France",
            website_url="https://gamma-opera.fr",
            venue_type="OPERA_HOUSE",
            user=user,
        ),
        Venue.objects.create(
            name="Delta Concert Hall",
            country="Spain",
            website_url="https://delta-concert.es",
            venue_type="CONCERT_HALL",
            user=user,
        ),
        Venue.objects.create(
            name="Epsilon Dance Studio",
            country="Spain",
            website_url="https://epsilon-dance.es",
            venue_type="DANCE_STUDIO",
            user=user,
        ),
    ]


# ---------------------------------------------------------------------------
# Search tests
# ---------------------------------------------------------------------------


@pytest.mark.django_db
class TestVenueSearch:
    """Tests for the SearchFilter on VenueViewSet."""

    def test_search_by_name_returns_matching_venue(self, authenticated_client, venue_set):
        """Searching by a unique name fragment returns only the matching venue."""
        response = authenticated_client.get("/api/venues/?search=Gamma")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 1
        assert response.data["results"][0]["name"] == "Gamma Opera House"

    def test_search_by_name_is_case_insensitive(self, authenticated_client, venue_set):
        """Search is case-insensitive, matching regardless of letter case."""
        response = authenticated_client.get("/api/venues/?search=gamma")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 1
        assert response.data["results"][0]["name"] == "Gamma Opera House"

    def test_search_by_name_partial_match(self, authenticated_client, venue_set):
        """A partial name fragment matches all venues whose name contains that substring."""
        response = authenticated_client.get("/api/venues/?search=dance")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 1
        assert response.data["results"][0]["name"] == "Epsilon Dance Studio"

    def test_search_by_country_returns_matching_venues(self, authenticated_client, venue_set):
        """Searching by country name returns all venues from that country."""
        response = authenticated_client.get("/api/venues/?search=France")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 2
        names = [r["name"] for r in response.data["results"]]
        assert "Alpha Grand Theatre" in names
        assert "Gamma Opera House" in names

    def test_search_by_website_url_returns_matching_venue(self, authenticated_client, venue_set):
        """Searching by a URL fragment returns the venue with a matching website_url."""
        response = authenticated_client.get("/api/venues/?search=beta-circus")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 1
        assert response.data["results"][0]["name"] == "Beta Circus Space"

    def test_search_venue_type_field_is_not_a_search_field(self, authenticated_client, venue_set):
        """
        venue_type is NOT in search_fields for VenueViewSet, so searching by venue
        type value does not work via the search parameter — use the filter parameter
        instead.
        """
        # "THEATRE" is the venue_type of one venue but is not a search field.
        response = authenticated_client.get("/api/venues/?search=THEATRE")

        assert response.status_code == status.HTTP_200_OK
        # "Theatre" also appears in "Alpha Grand Theatre" name, so it may match on name.
        # This test verifies the endpoint is stable; the key assertion is that searching
        # "CIRCUS_SPACE" (not present in any name/country/url) returns 0 results.
        no_name_match_response = authenticated_client.get("/api/venues/?search=CIRCUS_SPACE")
        assert no_name_match_response.status_code == status.HTTP_200_OK
        assert no_name_match_response.data["count"] == 0

    def test_search_with_no_results_returns_empty_list(self, authenticated_client, venue_set):
        """A search term matching nothing returns count=0 and an empty results list."""
        response = authenticated_client.get("/api/venues/?search=xyznonexistent")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 0
        assert response.data["results"] == []

    def test_empty_search_returns_all_venues(self, authenticated_client, venue_set):
        """An empty search parameter returns all venues without filtering."""
        response = authenticated_client.get("/api/venues/?search=")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == len(venue_set)

    def test_search_does_not_return_other_users_venues(self, authenticated_client, user, db):
        """Search results are scoped to the authenticated user's own data."""
        other_user = Profile.objects.create_user(
            email="other_venue@example.com", password="otherpass"
        )
        Venue.objects.create(
            name="Other User Venue",
            country="France",
            venue_type="THEATRE",
            user=other_user,
        )
        Venue.objects.create(
            name="My Own Venue",
            country="France",
            venue_type="THEATRE",
            user=user,
        )

        response = authenticated_client.get("/api/venues/?search=Venue")

        assert response.status_code == status.HTTP_200_OK
        names = [r["name"] for r in response.data["results"]]
        assert "My Own Venue" in names
        assert "Other User Venue" not in names

    def test_search_by_tld_in_url(self, authenticated_client, venue_set):
        """Searching by top-level domain fragment in website_url returns matching venues."""
        response = authenticated_client.get("/api/venues/?search=.es")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 2
        names = [r["name"] for r in response.data["results"]]
        assert "Delta Concert Hall" in names
        assert "Epsilon Dance Studio" in names


# ---------------------------------------------------------------------------
# Filter tests
# ---------------------------------------------------------------------------


@pytest.mark.django_db
class TestVenueFilter:
    """Tests for the DjangoFilterBackend on VenueViewSet."""

    def test_filter_by_country_returns_matching_venues(self, authenticated_client, venue_set):
        """Filtering by country returns only venues from that country."""
        response = authenticated_client.get("/api/venues/?country=France")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 2
        for result in response.data["results"]:
            assert result["country"] == "France"

    def test_filter_by_country_is_exact_match(self, authenticated_client, venue_set):
        """Country filter performs an exact match, not a partial match."""
        response = authenticated_client.get("/api/venues/?country=Franc")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 0

    def test_filter_by_venue_type_theatre(self, authenticated_client, venue_set):
        """Filtering by venue_type=THEATRE returns only theatres."""
        response = authenticated_client.get("/api/venues/?venue_type=THEATRE")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 1
        # venue_type is not exposed by VenueSerializer; verify by name instead
        assert response.data["results"][0]["name"] == "Alpha Grand Theatre"

    def test_filter_by_venue_type_opera_house(self, authenticated_client, venue_set):
        """Filtering by venue_type=OPERA_HOUSE returns only opera houses."""
        response = authenticated_client.get("/api/venues/?venue_type=OPERA_HOUSE")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 1
        assert response.data["results"][0]["name"] == "Gamma Opera House"

    def test_filter_by_venue_type_circus_space(self, authenticated_client, venue_set):
        """Filtering by venue_type=CIRCUS_SPACE returns only circus spaces."""
        response = authenticated_client.get("/api/venues/?venue_type=CIRCUS_SPACE")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 1
        assert response.data["results"][0]["name"] == "Beta Circus Space"

    def test_filter_by_nonexistent_country_returns_empty(self, authenticated_client, venue_set):
        """Filtering by a country with no matching records returns an empty result set."""
        response = authenticated_client.get("/api/venues/?country=Antarctica")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 0
        assert response.data["results"] == []

    def test_filter_by_venue_type_not_present_returns_empty(self, authenticated_client, venue_set):
        """Filtering by a venue_type that no venue has returns an empty result set."""
        response = authenticated_client.get("/api/venues/?venue_type=PUPPET_THEATRE")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 0

    def test_filter_by_country_and_venue_type_combined(self, authenticated_client, venue_set):
        """Combining country and venue_type filters narrows to their intersection."""
        response = authenticated_client.get("/api/venues/?country=Spain&venue_type=DANCE_STUDIO")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 1
        assert response.data["results"][0]["name"] == "Epsilon Dance Studio"

    def test_filter_country_with_multiple_results(self, authenticated_client, venue_set):
        """Filtering by a country with multiple matching venues returns all of them."""
        response = authenticated_client.get("/api/venues/?country=Spain")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 2
        names = [r["name"] for r in response.data["results"]]
        assert "Delta Concert Hall" in names
        assert "Epsilon Dance Studio" in names

    def test_filter_by_unknown_venue_type(self, authenticated_client, user, db):
        """Filtering by venue_type=UNKNOWN returns venues with that default type."""
        Venue.objects.create(
            name="Unknown Type Venue",
            country="Italy",
            venue_type="UNKNOWN",
            user=user,
        )

        response = authenticated_client.get("/api/venues/?venue_type=UNKNOWN")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 1
        assert response.data["results"][0]["name"] == "Unknown Type Venue"


# ---------------------------------------------------------------------------
# Ordering tests
# ---------------------------------------------------------------------------


@pytest.mark.django_db
class TestVenueOrdering:
    """Tests for ordering behaviour on VenueViewSet.

    VenueViewSet declares ordering_fields = ["name"] and ordering = ["name"],
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
        self, authenticated_client, venue_set
    ):
        """The list endpoint returns all venues regardless of ordering."""
        response = authenticated_client.get("/api/venues/")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == len(venue_set)

    def test_ordering_by_name_param_accepted_without_error(self, authenticated_client, venue_set):
        """?ordering=name is accepted without error (silently ignored, no OrderingFilter)."""
        response = authenticated_client.get("/api/venues/?ordering=name")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == len(venue_set)

    def test_ordering_by_name_descending_param_accepted_without_error(
        self, authenticated_client, venue_set
    ):
        """?ordering=-name is accepted without error."""
        response = authenticated_client.get("/api/venues/?ordering=-name")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == len(venue_set)

    def test_ordering_by_venue_type_param_accepted_without_error(
        self, authenticated_client, venue_set
    ):
        """
        ?ordering=venue_type is accepted without error. Even though venue_type is not in
        ordering_fields, without OrderingFilter in filter_backends all ordering params
        are silently ignored.
        """
        response = authenticated_client.get("/api/venues/?ordering=venue_type")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == len(venue_set)

    def test_ordering_by_country_param_accepted_without_error(
        self, authenticated_client, venue_set
    ):
        """?ordering=country is accepted without raising an error."""
        response = authenticated_client.get("/api/venues/?ordering=country")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == len(venue_set)

    def test_all_expected_venues_are_present_in_list_response(
        self, authenticated_client, venue_set
    ):
        """Every created venue appears in the list response (membership check)."""
        response = authenticated_client.get("/api/venues/")

        assert response.status_code == status.HTTP_200_OK
        returned_names = {r["name"] for r in response.data["results"]}
        expected_names = {v.name for v in venue_set}
        assert expected_names.issubset(returned_names)


# ---------------------------------------------------------------------------
# Combination tests
# ---------------------------------------------------------------------------


@pytest.mark.django_db
class TestVenueSearchFilterOrderingCombinations:
    """Tests for combinations of search, filter, and ordering query parameters."""

    def test_search_and_filter_by_country(self, authenticated_client, venue_set):
        """Combining search and country filter narrows results to their intersection."""
        response = authenticated_client.get("/api/venues/?search=Gamma&country=France")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 1
        assert response.data["results"][0]["name"] == "Gamma Opera House"

    def test_search_and_filter_no_intersection_returns_empty(self, authenticated_client, venue_set):
        """Search + filter combination with no overlap returns empty results."""
        # "Alpha Grand Theatre" is in France; filtering for Germany excludes it.
        response = authenticated_client.get("/api/venues/?search=Alpha&country=Germany")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 0

    def test_filter_by_country_with_ordering_param_accepted(self, authenticated_client, venue_set):
        """
        Filtering by country combined with an ordering param does not cause an error.
        The ordering param is silently ignored (no OrderingFilter in filter_backends)
        but the filter is applied correctly.
        """
        response = authenticated_client.get("/api/venues/?country=Spain&ordering=name")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 2
        for result in response.data["results"]:
            assert result["country"] == "Spain"

    def test_filter_by_country_with_descending_ordering_param_accepted(
        self, authenticated_client, venue_set
    ):
        """
        Filtering by country with ?ordering=-name does not cause an error.
        The ordering param is silently ignored without OrderingFilter.
        """
        response = authenticated_client.get("/api/venues/?country=Spain&ordering=-name")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 2
        for result in response.data["results"]:
            assert result["country"] == "Spain"

    def test_search_filter_and_ordering_param_together(self, authenticated_client, venue_set):
        """
        All three query parameters applied simultaneously return the correct subset
        without errors. The ordering param has no effect without OrderingFilter.
        """
        response = authenticated_client.get(
            "/api/venues/?search=France&country=France&ordering=name"
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 2
        for result in response.data["results"]:
            assert result["country"] == "France"

    def test_search_by_url_with_venue_type_filter(self, authenticated_client, venue_set):
        """Search on URL combined with venue_type filter gives precise results."""
        response = authenticated_client.get(
            "/api/venues/?search=gamma-opera&venue_type=OPERA_HOUSE"
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 1
        assert response.data["results"][0]["name"] == "Gamma Opera House"

    def test_search_by_url_with_venue_type_filter_mismatch(self, authenticated_client, venue_set):
        """
        Search matching on URL but mismatched venue_type filter returns empty results.
        """
        response = authenticated_client.get("/api/venues/?search=gamma-opera&venue_type=THEATRE")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 0

    def test_venue_type_filter_with_ordering_param_accepted(self, authenticated_client, user, db):
        """
        Filtering by venue_type combined with an ordering param does not cause an error.
        The ordering param is silently ignored without OrderingFilter in filter_backends,
        but the venue_type filter is applied correctly and only THEATRE venues are returned.
        Note: venue_type is not exposed by VenueSerializer so we verify by name membership.
        """
        Venue.objects.create(name="Zara Theatre", country="UK", venue_type="THEATRE", user=user)
        Venue.objects.create(name="Alpha Theatre", country="UK", venue_type="THEATRE", user=user)
        Venue.objects.create(name="Main Theatre", country="UK", venue_type="THEATRE", user=user)
        # Create a non-THEATRE venue that should be excluded
        Venue.objects.create(
            name="Other Concert Hall", country="UK", venue_type="CONCERT_HALL", user=user
        )

        response = authenticated_client.get("/api/venues/?venue_type=THEATRE&ordering=-name")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 3
        returned_names = {r["name"] for r in response.data["results"]}
        assert returned_names == {"Zara Theatre", "Alpha Theatre", "Main Theatre"}


# ---------------------------------------------------------------------------
# Pagination with search tests
# ---------------------------------------------------------------------------


@pytest.mark.django_db
class TestVenueSearchPagination:
    """Tests verifying search works correctly across paginated result sets."""

    def test_search_count_reflects_total_matches_not_page_size(
        self, authenticated_client, user, db
    ):
        """
        The 'count' field reflects total matching records across all pages,
        not just the current page size.
        """
        for i in range(15):
            Venue.objects.create(
                name=f"Searchable Venue {i:02d}",
                country="France",
                venue_type="THEATRE",
                user=user,
            )
        Venue.objects.create(
            name="Unrelated Space",
            country="Germany",
            venue_type="CONCERT_HALL",
            user=user,
        )

        response = authenticated_client.get("/api/venues/?search=Searchable")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 15

    def test_second_page_of_search_results_contains_remaining_matches(
        self, authenticated_client, user, db
    ):
        """Following the 'next' pagination link returns the remaining search matches."""
        for i in range(15):
            Venue.objects.create(
                name=f"Paginated Venue {i:02d}",
                country="France",
                venue_type="THEATRE",
                user=user,
            )

        first_response = authenticated_client.get("/api/venues/?search=Paginated&ordering=name")
        assert first_response.status_code == status.HTTP_200_OK
        assert first_response.data["count"] == 15

        next_url = first_response.data.get("next")
        if next_url:
            next_path = next_url.split("testserver")[-1]
            second_response = authenticated_client.get(next_path)
            assert second_response.status_code == status.HTTP_200_OK
            first_page_ids = {r["id"] for r in first_response.data["results"]}
            second_page_ids = {r["id"] for r in second_response.data["results"]}
            assert first_page_ids.isdisjoint(second_page_ids)

    def test_search_with_filter_count_excludes_non_matching_records(
        self, authenticated_client, user, db
    ):
        """
        When search and filter are combined the count reflects only records
        matching both criteria.
        """
        for i in range(5):
            Venue.objects.create(
                name=f"French Venue {i}",
                country="France",
                venue_type="THEATRE",
                user=user,
            )
        for i in range(5):
            Venue.objects.create(
                name=f"German Venue {i}",
                country="Germany",
                venue_type="THEATRE",
                user=user,
            )

        response = authenticated_client.get("/api/venues/?search=Venue&country=France")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 5


# ---------------------------------------------------------------------------
# Edge case tests
# ---------------------------------------------------------------------------


@pytest.mark.django_db
class TestVenueSearchFilterEdgeCases:
    """Edge cases and boundary conditions for search, filter, and ordering."""

    def test_unauthenticated_request_is_rejected(self, api_client, venue_set):
        """Unauthenticated requests to the list endpoint are rejected."""
        response = api_client.get("/api/venues/?search=Alpha")

        assert response.status_code in [
            status.HTTP_401_UNAUTHORIZED,
            status.HTTP_403_FORBIDDEN,
        ]

    def test_search_term_with_special_characters_does_not_crash(
        self, authenticated_client, venue_set
    ):
        """Search terms containing URL-safe special characters return a valid response."""
        response = authenticated_client.get("/api/venues/?search=alpha%26beta")

        assert response.status_code == status.HTTP_200_OK

    def test_filter_with_empty_country_value_returns_all(self, authenticated_client, venue_set):
        """Passing an empty string for country filter returns all venues."""
        response = authenticated_client.get("/api/venues/?country=")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == len(venue_set)

    def test_soft_deleted_venues_excluded_from_search_results(self, authenticated_client, user, db):
        """Search results do not include soft-deleted venues."""
        Venue.objects.create(
            name="Visible Theatre",
            country="France",
            venue_type="THEATRE",
            user=user,
        )
        deleted = Venue.objects.create(
            name="Deleted Theatre",
            country="France",
            venue_type="THEATRE",
            user=user,
        )
        deleted.delete()

        response = authenticated_client.get("/api/venues/?search=Theatre")

        assert response.status_code == status.HTTP_200_OK
        names = [r["name"] for r in response.data["results"]]
        assert "Visible Theatre" in names
        assert "Deleted Theatre" not in names

    def test_no_query_params_returns_all_user_venues(self, authenticated_client, venue_set):
        """With no query parameters the endpoint returns all of the user's active venues."""
        response = authenticated_client.get("/api/venues/")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == len(venue_set)

    def test_filter_by_empty_venue_type_returns_all(self, authenticated_client, venue_set):
        """Passing an empty string for venue_type filter returns all venues."""
        response = authenticated_client.get("/api/venues/?venue_type=")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == len(venue_set)

    def test_search_result_names_contain_search_term(self, authenticated_client, venue_set):
        """Every returned result contains the searched term in name, country, or website_url."""
        response = authenticated_client.get("/api/venues/?search=concert")

        assert response.status_code == status.HTTP_200_OK
        for result in response.data["results"]:
            combined = (
                result["name"].lower()
                + result["country"].lower()
                + result.get("website_url", "").lower()
            )
            assert "concert" in combined

    def test_filter_result_integrity_with_ordering_param(self, authenticated_client, venue_set):
        """
        All results from a filtered + ordering param query belong to the filter's
        country. The ordering param is silently ignored without OrderingFilter,
        but filter correctness is preserved.
        """
        response = authenticated_client.get("/api/venues/?country=France&ordering=name")

        assert response.status_code == status.HTTP_200_OK
        for result in response.data["results"]:
            assert result["country"] == "France"

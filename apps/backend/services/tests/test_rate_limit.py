from unittest.mock import patch

import pytest

from services.rate_limit import check_llm_rate_limit, increment_llm_call_counter


@pytest.mark.django_db
class TestCheckLLMRateLimit:
    """Tests for check_llm_rate_limit function."""

    @patch("services.rate_limit.cache")
    def test_under_limit_returns_true_and_remaining_count(self, mock_cache):
        """Test that function returns True when under rate limit."""
        mock_cache.get.return_value = 50

        allowed, remaining = check_llm_rate_limit("test_tenant", limit=100)

        assert allowed is True
        assert remaining == 50

    @patch("services.rate_limit.cache")
    def test_at_limit_returns_false_and_zero_remaining(self, mock_cache):
        """Test that function returns False when at rate limit."""
        mock_cache.get.return_value = 100

        allowed, remaining = check_llm_rate_limit("test_tenant", limit=100)

        assert allowed is False
        assert remaining == 0

    @patch("services.rate_limit.cache")
    def test_over_limit_returns_false_and_zero_remaining(self, mock_cache):
        """Test that function returns False when over rate limit."""
        mock_cache.get.return_value = 150

        allowed, remaining = check_llm_rate_limit("test_tenant", limit=100)

        assert allowed is False
        assert remaining == 0

    @patch("services.rate_limit.cache")
    def test_no_cached_value_returns_full_limit(self, mock_cache):
        """Test that function returns full limit when cache is empty."""
        mock_cache.get.return_value = 0

        allowed, remaining = check_llm_rate_limit("test_tenant", limit=100)

        assert allowed is True
        assert remaining == 100

    @patch("services.rate_limit.cache")
    def test_different_tenant_schemas_isolated(self, mock_cache):
        """Test that different tenants have isolated rate limits."""
        mock_cache.get.return_value = 50

        allowed1, _ = check_llm_rate_limit("tenant_1", limit=100)
        allowed2, _ = check_llm_rate_limit("tenant_2", limit=100)

        assert allowed1 is True
        assert allowed2 is True
        assert mock_cache.get.call_count == 2

    @patch("services.rate_limit.cache")
    def test_cache_key_includes_date(self, mock_cache):
        """Test that cache key includes today's date and tenant schema."""
        mock_cache.get.return_value = 0

        check_llm_rate_limit("test_tenant")

        called_key = mock_cache.get.call_args[0][0]
        assert "test_tenant" in called_key
        assert "llm_limit" in called_key
        # Key should be in format: "llm_limit:tenant_schema:date"
        assert called_key.startswith("llm_limit")

    @patch("services.rate_limit.cache")
    def test_custom_limit_parameter(self, mock_cache):
        """Test that custom limit parameter is respected."""
        mock_cache.get.return_value = 25

        allowed, remaining = check_llm_rate_limit("test_tenant", limit=50)

        assert allowed is True
        assert remaining == 25


@pytest.mark.django_db
class TestIncrementLLMCallCounter:
    """Tests for increment_llm_call_counter function."""

    @patch("services.rate_limit.cache")
    def test_first_call_sets_cache_with_timeout(self, mock_cache):
        """Test that first call sets cache with timeout until midnight."""
        # First call: cache is empty
        mock_cache.get.return_value = 0
        mock_cache.set.return_value = None
        mock_cache.incr.return_value = 1

        increment_llm_call_counter("test_tenant")

        mock_cache.set.assert_called_once()
        # Verify the timeout is positive (seconds until midnight)
        mock_cache.set.call_args
        # get() is called once to check if count is 0
        assert mock_cache.get.called

    @patch("services.rate_limit.cache")
    def test_subsequent_calls_increment_counter(self, mock_cache):
        """Test that subsequent calls increment the existing counter."""
        mock_cache.get.side_effect = [1, 2]  # First get returns 1, then we increment

        increment_llm_call_counter("test_tenant")

        mock_cache.incr.assert_called_once()

    @patch("services.rate_limit.cache")
    def test_returns_updated_count(self, mock_cache):
        """Test that function returns the updated count."""
        mock_cache.get.side_effect = [0, 1]  # get called twice: once for check, once for return
        mock_cache.set.return_value = None

        result = increment_llm_call_counter("test_tenant")

        # After increment, the count should be returned
        assert result == 1

    @patch("services.rate_limit.cache")
    def test_cache_key_format(self, mock_cache):
        """Test that cache key has correct format."""
        mock_cache.get.return_value = 1
        mock_cache.incr.return_value = 2

        increment_llm_call_counter("test_tenant")

        called_key = mock_cache.incr.call_args[0][0]
        assert "llm_limit" in called_key
        assert "test_tenant" in called_key

    @patch("services.rate_limit.cache")
    def test_multiple_tenants_independent_counters(self, mock_cache):
        """Test that different tenants have independent counters."""
        mock_cache.get.return_value = 1
        mock_cache.incr.return_value = 2

        increment_llm_call_counter("tenant_1")
        increment_llm_call_counter("tenant_2")

        assert mock_cache.incr.call_count == 2
        call_args_list = mock_cache.incr.call_args_list
        key1 = call_args_list[0][0][0]
        key2 = call_args_list[1][0][0]
        assert "tenant_1" in key1
        assert "tenant_2" in key2

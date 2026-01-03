#!/usr/bin/env python3
"""
Unit tests for rate limiting functionality in GroqProvider
"""

import pytest
from unittest.mock import Mock, MagicMock
from groqqy.providers.groq import GroqProvider, RetryConfig


@pytest.fixture
def provider():
    """Create GroqProvider instance for testing"""
    # Mock the API key to avoid needing env var
    provider = GroqProvider.__new__(GroqProvider)
    provider.model = "llama-3.1-8b-instant"
    provider.api_key = "test-key"
    provider.system_message = None
    provider.temperature = 0.5
    provider.top_p = 0.65
    provider.lenient_tool_parsing = True
    provider.lenient_parse_count = 0
    provider.max_retries = 3
    provider.initial_backoff = 1.0
    provider.backoff_multiplier = 2.0
    provider.max_backoff = 60.0
    provider.retry_count = 0
    return provider


class TestCalculateBackoff:
    """Test _calculate_backoff method"""

    def test_exponential_backoff_first_attempt(self, provider):
        """Test backoff on first retry (attempt=0)"""
        wait_time = provider._calculate_backoff(0)
        assert wait_time == 1.0  # initial_backoff * (2^0) = 1.0 * 1

    def test_exponential_backoff_second_attempt(self, provider):
        """Test backoff on second retry (attempt=1)"""
        wait_time = provider._calculate_backoff(1)
        assert wait_time == 2.0  # initial_backoff * (2^1) = 1.0 * 2

    def test_exponential_backoff_third_attempt(self, provider):
        """Test backoff on third retry (attempt=2)"""
        wait_time = provider._calculate_backoff(2)
        assert wait_time == 4.0  # initial_backoff * (2^2) = 1.0 * 4

    def test_exponential_backoff_with_cap(self, provider):
        """Test backoff respects max_backoff cap"""
        provider.max_backoff = 5.0
        wait_time = provider._calculate_backoff(10)  # Would be 1024 without cap
        assert wait_time == 5.0

    def test_api_suggested_wait_time(self, provider):
        """Test using API-suggested wait time"""
        wait_time = provider._calculate_backoff(0, suggested_wait=8.12)
        assert wait_time == 8.12

    def test_api_suggested_wait_time_capped(self, provider):
        """Test API suggestion respects max_backoff cap"""
        provider.max_backoff = 5.0
        wait_time = provider._calculate_backoff(0, suggested_wait=100.0)
        assert wait_time == 5.0  # Capped at max_backoff

    def test_custom_multiplier(self, provider):
        """Test with custom backoff multiplier"""
        provider.backoff_multiplier = 3.0
        wait_time = provider._calculate_backoff(2)
        assert wait_time == 9.0  # 1.0 * (3^2) = 9.0

    def test_custom_initial_backoff(self, provider):
        """Test with custom initial backoff"""
        provider.initial_backoff = 2.0
        wait_time = provider._calculate_backoff(1)
        assert wait_time == 4.0  # 2.0 * (2^1) = 4.0


class TestExtractRetryAfter:
    """Test _extract_retry_after method"""

    def test_extract_from_header(self, provider):
        """Test extracting retry-after from response header"""
        response = Mock()
        response.headers = {'retry-after': '5.0'}
        error_data = {}

        wait_time = provider._extract_retry_after(response, error_data)
        assert wait_time == 5.0

    def test_extract_from_error_message(self, provider):
        """Test extracting wait time from error message"""
        response = Mock()
        response.headers = {}
        error_data = {
            'error': {
                'message': 'Rate limit reached. Please try again in 8.12s'
            }
        }

        wait_time = provider._extract_retry_after(response, error_data)
        assert wait_time == 8.12

    def test_header_takes_precedence(self, provider):
        """Test retry-after header takes precedence over message"""
        response = Mock()
        response.headers = {'retry-after': '3.0'}
        error_data = {
            'error': {
                'message': 'Please try again in 10.0s'
            }
        }

        wait_time = provider._extract_retry_after(response, error_data)
        assert wait_time == 3.0  # From header, not message

    def test_no_retry_info(self, provider):
        """Test when no retry info is available"""
        response = Mock()
        response.headers = {}
        error_data = {'error': {'message': 'Generic error'}}

        wait_time = provider._extract_retry_after(response, error_data)
        assert wait_time is None

    def test_invalid_header_value(self, provider):
        """Test handling invalid header value"""
        response = Mock()
        response.headers = {'retry-after': 'invalid'}
        error_data = {}

        wait_time = provider._extract_retry_after(response, error_data)
        assert wait_time is None

    def test_malformed_error_message(self, provider):
        """Test handling malformed error message"""
        response = Mock()
        response.headers = {}
        error_data = {
            'error': {
                'message': 'Rate limit reached'  # No wait time
            }
        }

        wait_time = provider._extract_retry_after(response, error_data)
        assert wait_time is None


class TestCreateSyntheticResponse:
    """Test _create_synthetic_response method"""

    def test_synthetic_response_structure(self, provider):
        """Test synthetic response has correct structure"""
        tool_calls = [{
            "id": "call_1",
            "type": "function",
            "function": {"name": "test", "arguments": "{}"}
        }]
        failed_gen = "original failed output"

        response = provider._create_synthetic_response(tool_calls, failed_gen)

        assert "choices" in response
        assert "usage" in response
        assert "model" in response
        assert response["model"] == "llama-3.1-8b-instant"
        assert response["_lenient_parse"] is True
        assert response["_original_error"] == failed_gen

    def test_synthetic_response_tool_calls(self, provider):
        """Test synthetic response includes tool calls"""
        tool_calls = [{
            "id": "call_1",
            "type": "function",
            "function": {"name": "read_file", "arguments": '{"path": "/test"}'}
        }]

        response = provider._create_synthetic_response(tool_calls, "")
        message = response["choices"][0]["message"]

        assert message["role"] == "assistant"
        assert message["content"] is None
        assert message["tool_calls"] == tool_calls

    def test_synthetic_response_usage_zeros(self, provider):
        """Test synthetic response has zero usage (unknown)"""
        response = provider._create_synthetic_response([], "")
        usage = response["usage"]

        assert usage["prompt_tokens"] == 0
        assert usage["completion_tokens"] == 0
        assert usage["total_tokens"] == 0


class TestRetryConfigIntegration:
    """Test RetryConfig integration with GroqProvider"""

    def test_default_retry_config(self):
        """Test provider with default retry config"""
        provider = GroqProvider.__new__(GroqProvider)
        provider.api_key = "test"
        config = RetryConfig()

        provider.max_retries = config.max_retries
        provider.initial_backoff = config.initial_backoff
        provider.backoff_multiplier = config.backoff_multiplier
        provider.max_backoff = config.max_backoff

        assert provider.max_retries == 3
        assert provider.initial_backoff == 1.0

    def test_custom_retry_config(self):
        """Test provider with custom retry config"""
        provider = GroqProvider.__new__(GroqProvider)
        provider.api_key = "test"
        config = RetryConfig(
            max_retries=5,
            initial_backoff=2.0,
            backoff_multiplier=3.0,
            max_backoff=120.0
        )

        provider.max_retries = config.max_retries
        provider.initial_backoff = config.initial_backoff
        provider.backoff_multiplier = config.backoff_multiplier
        provider.max_backoff = config.max_backoff

        assert provider.max_retries == 5
        assert provider.initial_backoff == 2.0
        assert provider.backoff_multiplier == 3.0
        assert provider.max_backoff == 120.0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

#!/usr/bin/env python3
"""
Integration tests for rate limit retry flow with mocked HTTP responses
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import time
from groqqy.providers.groq import GroqProvider, RetryConfig


@pytest.fixture
def provider_with_retry():
    """Create GroqProvider with fast retry config for testing"""
    with patch.object(GroqProvider, '_get_api_key', return_value='test-key'):
        config = RetryConfig(
            max_retries=3,
            initial_backoff=0.01,  # Fast for testing
            backoff_multiplier=2.0,
            max_backoff=0.1
        )
        return GroqProvider(retry_config=config)


class TestRateLimitRetry:
    """Test rate limit retry behavior"""

    @patch('groqqy.providers.groq.requests.post')
    def test_successful_retry_after_rate_limit(self, mock_post, provider_with_retry):
        """Test successful retry after rate limit error"""
        # First call: 429 rate limit
        rate_limit_response = Mock()
        rate_limit_response.ok = False
        rate_limit_response.status_code = 429
        rate_limit_response.text = '{"error": {"message": "Rate limit exceeded"}}'
        rate_limit_response.json.return_value = {
            'error': {'message': 'Rate limit exceeded'}
        }
        rate_limit_response.headers = {}

        # Second call: Success
        success_response = Mock()
        success_response.ok = True
        success_response.json.return_value = {
            'choices': [{
                'message': {'role': 'assistant', 'content': 'Success'},
                'finish_reason': 'stop'
            }],
            'usage': {'prompt_tokens': 10, 'completion_tokens': 5}
        }

        mock_post.side_effect = [rate_limit_response, success_response]

        # Should retry and succeed
        result = provider_with_retry._call_api({'model': 'test'})

        assert result['choices'][0]['message']['content'] == 'Success'
        assert mock_post.call_count == 2
        assert provider_with_retry.retry_count == 1

    @patch('groqqy.providers.groq.requests.post')
    @patch('groqqy.providers.groq.time.sleep')
    def test_retry_uses_api_suggested_wait_time(
        self,
        mock_sleep,
        mock_post,
        provider_with_retry
    ):
        """Test retry uses API-suggested wait time"""
        # Rate limit with suggested wait time
        rate_limit_response = Mock()
        rate_limit_response.ok = False
        rate_limit_response.status_code = 429
        rate_limit_response.text = 'error'
        rate_limit_response.json.return_value = {
            'error': {'message': 'Please try again in 0.05s'}
        }
        rate_limit_response.headers = {}

        success_response = Mock()
        success_response.ok = True
        success_response.json.return_value = {
            'choices': [{'message': {'content': 'ok'}}],
            'usage': {}
        }

        mock_post.side_effect = [rate_limit_response, success_response]

        provider_with_retry._call_api({'model': 'test'})

        # Should sleep for API-suggested time (capped at max_backoff=0.1)
        mock_sleep.assert_called_once()
        sleep_time = mock_sleep.call_args[0][0]
        assert sleep_time == 0.05  # API suggested, under cap

    @patch('groqqy.providers.groq.requests.post')
    def test_retry_exhausted_raises_error(self, mock_post, provider_with_retry):
        """Test error raised after max retries exhausted"""
        # All calls return 429
        rate_limit_response = Mock()
        rate_limit_response.ok = False
        rate_limit_response.status_code = 429
        rate_limit_response.text = 'error'
        rate_limit_response.json.return_value = {
            'error': {'message': 'Rate limit exceeded'}
        }
        rate_limit_response.headers = {}

        mock_post.return_value = rate_limit_response

        # Should raise after max_retries attempts
        with pytest.raises(RuntimeError) as exc_info:
            provider_with_retry._call_api({'model': 'test'})

        assert "Rate limit exceeded after 3 attempts" in str(exc_info.value)
        assert mock_post.call_count == 3
        assert provider_with_retry.retry_count == 3

    @patch('groqqy.providers.groq.requests.post')
    @patch('groqqy.providers.groq.time.sleep')
    def test_exponential_backoff_progression(
        self,
        mock_sleep,
        mock_post,
        provider_with_retry
    ):
        """Test exponential backoff time progression"""
        # Two 429s, then success
        rate_limit_response = Mock()
        rate_limit_response.ok = False
        rate_limit_response.status_code = 429
        rate_limit_response.text = 'error'
        rate_limit_response.json.return_value = {'error': {'message': 'Rate limit'}}
        rate_limit_response.headers = {}

        success_response = Mock()
        success_response.ok = True
        success_response.json.return_value = {
            'choices': [{'message': {'content': 'ok'}}],
            'usage': {}
        }

        mock_post.side_effect = [
            rate_limit_response,
            rate_limit_response,
            success_response
        ]

        provider_with_retry._call_api({'model': 'test'})

        # Check exponential backoff: 0.01, 0.02
        assert mock_sleep.call_count == 2
        sleep_calls = [call[0][0] for call in mock_sleep.call_args_list]
        assert sleep_calls[0] == 0.01  # initial_backoff * (2^0)
        assert sleep_calls[1] == 0.02  # initial_backoff * (2^1)

    @patch('groqqy.providers.groq.requests.post')
    def test_retry_count_tracking(self, mock_post, provider_with_retry):
        """Test retry_count is correctly tracked across calls"""
        rate_limit = Mock()
        rate_limit.ok = False
        rate_limit.status_code = 429
        rate_limit.text = 'error'
        rate_limit.json.return_value = {'error': {'message': 'Rate limit'}}
        rate_limit.headers = {}

        success = Mock()
        success.ok = True
        success.json.return_value = {'choices': [{'message': {}}], 'usage': {}}

        # First call: 1 retry
        mock_post.side_effect = [rate_limit, success]
        provider_with_retry._call_api({'model': 'test'})
        assert provider_with_retry.retry_count == 1

        # Second call: 2 more retries (cumulative = 3)
        mock_post.side_effect = [rate_limit, rate_limit, success]
        provider_with_retry._call_api({'model': 'test'})
        assert provider_with_retry.retry_count == 3


class TestToolUseErrorHandling:
    """Test tool use error handling with lenient parsing"""

    @patch('groqqy.providers.groq.requests.post')
    def test_lenient_parsing_recovery(self, mock_post, provider_with_retry):
        """Test successful recovery via lenient parsing"""
        # 400 error with malformed tool call
        error_response = Mock()
        error_response.ok = False
        error_response.status_code = 400
        error_response.text = 'error'
        error_response.json.return_value = {
            'error': {
                'message': 'tool_use_failed',
                'failed_generation': '<function=read_file>{"path": "/test"}</function>'
            }
        }

        mock_post.return_value = error_response

        payload = {
            'model': 'test',
            'tools': [{
                'type': 'function',
                'function': {
                    'name': 'read_file',
                    'parameters': {}
                }
            }]
        }

        # Should recover and return synthetic response
        result = provider_with_retry._call_api(payload)

        assert result['_lenient_parse'] is True
        assert len(result['choices'][0]['message']['tool_calls']) == 1
        assert provider_with_retry.lenient_parse_count == 1

    @patch('groqqy.providers.groq.requests.post')
    def test_lenient_parsing_disabled(self, mock_post):
        """Test error raised when lenient parsing disabled"""
        with patch.object(GroqProvider, '_get_api_key', return_value='test-key'):
            provider = GroqProvider(lenient_tool_parsing=False)

        error_response = Mock()
        error_response.ok = False
        error_response.status_code = 400
        error_response.text = 'error'
        error_response.json.return_value = {
            'error': {
                'message': 'tool_use_failed',
                'failed_generation': 'malformed'
            }
        }

        mock_post.return_value = error_response

        payload = {'model': 'test', 'tools': []}

        with pytest.raises(RuntimeError) as exc_info:
            provider._call_api(payload)

        assert "tool_use_failed" in str(exc_info.value)
        assert "Lenient parsing is disabled" in str(exc_info.value)


class TestGenericErrors:
    """Test handling of generic (non-retryable) errors"""

    @patch('groqqy.providers.groq.requests.post')
    def test_500_error_not_retried(self, mock_post, provider_with_retry):
        """Test 500 error is not retried"""
        error_response = Mock()
        error_response.ok = False
        error_response.status_code = 500
        error_response.text = 'error'
        error_response.json.return_value = {
            'error': {'message': 'Internal server error'}
        }

        mock_post.return_value = error_response

        with pytest.raises(RuntimeError) as exc_info:
            provider_with_retry._call_api({'model': 'test'})

        assert "500" in str(exc_info.value)
        assert mock_post.call_count == 1  # Not retried

    @patch('groqqy.providers.groq.requests.post')
    def test_401_error_not_retried(self, mock_post, provider_with_retry):
        """Test 401 auth error is not retried"""
        error_response = Mock()
        error_response.ok = False
        error_response.status_code = 401
        error_response.text = 'error'
        error_response.json.return_value = {
            'error': {'message': 'Invalid API key'}
        }

        mock_post.return_value = error_response

        with pytest.raises(RuntimeError) as exc_info:
            provider_with_retry._call_api({'model': 'test'})

        assert "401" in str(exc_info.value)
        assert mock_post.call_count == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

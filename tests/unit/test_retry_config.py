#!/usr/bin/env python3
"""
Unit tests for RetryConfig dataclass
"""

import pytest
from groqqy import RetryConfig


def test_retry_config_defaults():
    """Test RetryConfig with default values"""
    config = RetryConfig()

    assert config.max_retries == 3
    assert config.initial_backoff == 1.0
    assert config.backoff_multiplier == 2.0
    assert config.max_backoff == 60.0


def test_retry_config_custom_values():
    """Test RetryConfig with custom values"""
    config = RetryConfig(
        max_retries=5,
        initial_backoff=2.0,
        backoff_multiplier=3.0,
        max_backoff=120.0
    )

    assert config.max_retries == 5
    assert config.initial_backoff == 2.0
    assert config.backoff_multiplier == 3.0
    assert config.max_backoff == 120.0


def test_retry_config_partial_override():
    """Test RetryConfig with partial override"""
    config = RetryConfig(max_retries=10)

    assert config.max_retries == 10
    assert config.initial_backoff == 1.0  # Default
    assert config.backoff_multiplier == 2.0  # Default
    assert config.max_backoff == 60.0  # Default


def test_retry_config_testing_preset():
    """Test RetryConfig preset for testing (fast retries)"""
    config = RetryConfig(
        max_retries=2,
        initial_backoff=0.1,
        backoff_multiplier=1.5,
        max_backoff=1.0
    )

    assert config.max_retries == 2
    assert config.initial_backoff == 0.1
    assert config.backoff_multiplier == 1.5
    assert config.max_backoff == 1.0


def test_retry_config_production_preset():
    """Test RetryConfig preset for production (conservative)"""
    config = RetryConfig(
        max_retries=5,
        initial_backoff=2.0,
        backoff_multiplier=2.0,
        max_backoff=120.0
    )

    assert config.max_retries == 5
    assert config.initial_backoff == 2.0
    assert config.backoff_multiplier == 2.0
    assert config.max_backoff == 120.0


def test_retry_config_equality():
    """Test RetryConfig equality comparison"""
    config1 = RetryConfig(max_retries=3)
    config2 = RetryConfig(max_retries=3)
    config3 = RetryConfig(max_retries=5)

    assert config1 == config2
    assert config1 != config3


def test_retry_config_repr():
    """Test RetryConfig string representation"""
    config = RetryConfig()
    repr_str = repr(config)

    assert "RetryConfig" in repr_str
    assert "max_retries=3" in repr_str
    assert "initial_backoff=1.0" in repr_str


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

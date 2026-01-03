# Groqqy Test Suite

**Comprehensive testing for the Groqqy agentic bot library**

## Overview

The Groqqy test suite ensures code quality, prevents regressions, and validates functionality across all components. Tests are organized by type and use mocking to avoid real API calls.

**Current Coverage:**
- **76% coverage** of `groq.py` (rate limiting and retry logic)
- **35 passing tests** across unit and integration categories
- **0.21s** total runtime (fast feedback)
- **100% pass rate** on all test runs

---

## Test Organization

```
tests/
├── unit/                           # Unit tests (isolated component testing)
│   ├── test_retry_config.py       # RetryConfig dataclass (7 tests)
│   └── test_rate_limiting.py      # Rate limiting logic (19 tests)
├── integration/                    # Integration tests (end-to-end flows)
│   └── test_retry_flow.py         # Retry flow integration (9 tests)
└── examples/                       # Example validation tests
```

### Test Categories

**Unit Tests** (`tests/unit/`):
- Test individual functions and classes in isolation
- Use mocks to eliminate external dependencies
- Fast execution (0.11s for all unit tests)
- Focus on edge cases and boundary conditions

**Integration Tests** (`tests/integration/`):
- Test interactions between components
- Validate end-to-end workflows
- Mock external APIs but test internal integration
- Runtime: 0.21s for all integration tests

**Example Tests** (`tests/examples/`):
- Validate that example scripts work as documented
- Ensure examples stay in sync with library changes

---

## Running Tests

### All Tests

```bash
# From project root
pytest

# With verbose output
pytest -v

# With coverage report
pytest --cov=groqqy --cov-report=term-missing
```

### Specific Test Categories

```bash
# Unit tests only (fast)
pytest tests/unit/ -v

# Integration tests only
pytest tests/integration/ -v

# Example validation
pytest tests/examples/ -v
```

### Specific Test Files

```bash
# RetryConfig tests
pytest tests/unit/test_retry_config.py -v

# Rate limiting tests
pytest tests/unit/test_rate_limiting.py -v

# Retry flow integration
pytest tests/integration/test_retry_flow.py -v
```

### Coverage Analysis

```bash
# Generate coverage report
pytest --cov=groqqy.providers.groq --cov-report=term-missing

# Coverage for specific module
pytest tests/unit/test_rate_limiting.py --cov=groqqy.providers.groq --cov-report=term-missing

# HTML coverage report (opens in browser)
pytest --cov=groqqy --cov-report=html
open htmlcov/index.html
```

---

## Test Structure

### Unit Test Example

```python
# tests/unit/test_retry_config.py

import pytest
from groqqy.providers.groq import RetryConfig

def test_default_values():
    """Test RetryConfig default values."""
    config = RetryConfig()

    assert config.max_retries == 3
    assert config.initial_backoff == 1.0
    assert config.backoff_multiplier == 2.0
    assert config.max_backoff == 60.0

def test_custom_values():
    """Test RetryConfig with custom values."""
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
```

### Integration Test Example

```python
# tests/integration/test_retry_flow.py

import pytest
from unittest.mock import Mock, patch
from groqqy.providers.groq import GroqProvider

@patch('groqqy.providers.groq.time.sleep')  # Mock sleep to speed up tests
@patch('groqqy.providers.groq.requests.post')
def test_successful_retry_after_rate_limit(mock_post, mock_sleep):
    """Test successful retry after 429 rate limit."""
    # First call: rate limit (429)
    mock_response_429 = Mock()
    mock_response_429.ok = False
    mock_response_429.status_code = 429
    mock_response_429.headers = {'retry-after': '2'}
    mock_response_429.text = '{"error": {"message": "Rate limit exceeded"}}'
    mock_response_429.json.return_value = {"error": {"message": "Rate limit exceeded"}}

    # Second call: success (200)
    mock_response_200 = Mock()
    mock_response_200.ok = True
    mock_response_200.json.return_value = {
        "choices": [{"message": {"content": "Success!", "role": "assistant"}}],
        "usage": {"prompt_tokens": 10, "completion_tokens": 5}
    }

    mock_post.side_effect = [mock_response_429, mock_response_200]

    provider = GroqProvider(model="llama-3.1-8b-instant")
    result = provider.chat([{"role": "user", "content": "test"}])

    assert result.text == "Success!"
    assert provider.retry_count == 1
    mock_sleep.assert_called_once_with(2.0)  # Slept for suggested time
```

---

## Mocking Strategy

### Why Mock?

- **Deterministic**: Tests produce consistent results
- **Fast**: No network calls or API rate limits
- **Cost**: No API charges during testing
- **Isolation**: Test code logic, not external services
- **Reliability**: Tests don't fail due to network issues

### What We Mock

1. **API Calls** (`requests.post`):
   - Mock HTTP responses (200, 429, 400, 500)
   - Control response data for different scenarios
   - Simulate error conditions

2. **Time** (`time.sleep`):
   - Speed up tests that use backoff delays
   - Verify sleep was called with correct duration
   - Keep test runtime under 1 second

3. **External Tools** (file system, commands):
   - Use temporary files or in-memory data
   - Mock subprocess calls
   - Control external dependencies

### Mocking Best Practices

```python
from unittest.mock import Mock, patch

# Mock at the usage site (where it's imported)
@patch('groqqy.providers.groq.requests.post')  # ✅ Correct
@patch('requests.post')                         # ❌ Wrong (won't work)

# Create realistic mock responses
mock_response = Mock()
mock_response.ok = True
mock_response.status_code = 200
mock_response.json.return_value = {"key": "value"}

# Verify mocks were called correctly
mock_post.assert_called_once()
mock_sleep.assert_called_with(2.0)
```

---

## Writing New Tests

### Test Naming Convention

```python
# Format: test_<what>_<scenario>
def test_retry_config_default_values():        # ✅ Clear
def test_calculate_backoff_exponential():      # ✅ Descriptive
def test_rate_limit_retry_exhaustion():        # ✅ Specific

def test_config():                             # ❌ Vague
def test_1():                                  # ❌ No context
```

### Test Structure (AAA Pattern)

```python
def test_calculate_backoff_with_api_suggestion():
    # Arrange: Set up test data and mocks
    provider = GroqProvider(model="test-model")

    # Act: Execute the code being tested
    backoff = provider._calculate_backoff(attempt=0, suggested_wait=5.0)

    # Assert: Verify expected behavior
    assert backoff == 5.0
```

### Coverage Expectations

**For new code:**
- Critical paths: 100% coverage required
- Error handling: All branches tested
- Edge cases: Documented and tested
- Overall: >75% coverage for production code

**For bug fixes:**
- Add test that reproduces the bug
- Verify fix resolves the issue
- Ensure regression doesn't occur

### Adding Tests for New Features

1. **Create test file** in appropriate category:
   ```bash
   # Unit test
   touch tests/unit/test_new_feature.py

   # Integration test
   touch tests/integration/test_new_feature_integration.py
   ```

2. **Write tests** using existing patterns:
   - Import necessary modules
   - Set up fixtures if needed
   - Write clear test functions
   - Use mocks for external dependencies

3. **Run tests** to verify:
   ```bash
   pytest tests/unit/test_new_feature.py -v
   ```

4. **Check coverage**:
   ```bash
   pytest tests/unit/test_new_feature.py --cov=groqqy.module --cov-report=term-missing
   ```

---

## Test Data and Fixtures

### Using Fixtures

```python
import pytest

@pytest.fixture
def provider():
    """Fixture providing a GroqProvider instance."""
    return GroqProvider(model="test-model")

def test_with_fixture(provider):
    """Test using the provider fixture."""
    assert provider.model == "test-model"
```

### Temporary Files

```python
import tempfile

def test_read_file():
    with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
        f.write("test content")
        path = f.name

    result = read_file(path)
    assert result == "test content"
```

---

## Continuous Integration

Tests run automatically on every commit via GitHub Actions.

**CI Configuration** (`.github/workflows/test.yml`):
- Run all tests on Python 3.8, 3.9, 3.10, 3.11
- Generate coverage reports
- Block merges if tests fail or coverage drops below threshold

**Local Pre-Commit Hook** (optional):
```bash
#!/bin/bash
# .git/hooks/pre-commit
pytest
if [ $? -ne 0 ]; then
    echo "Tests failed. Commit aborted."
    exit 1
fi
```

---

## Debugging Failed Tests

### Verbose Output

```bash
# See detailed test output
pytest -v

# Show print statements
pytest -s

# Stop at first failure
pytest -x
```

### Running Single Test

```bash
# Run one test function
pytest tests/unit/test_retry_config.py::test_default_values -v
```

### Using pdb

```python
def test_something():
    # Drop into debugger
    import pdb; pdb.set_trace()

    # Test continues after debugging
    assert result == expected
```

---

## Test Metrics

### Current Status (v2.5.0)

| Metric | Value | Status |
|--------|-------|--------|
| Total tests | 35 | ✅ |
| Pass rate | 100% | ✅ |
| Runtime | 0.21s | ✅ Fast |
| Coverage (groq.py) | 76% | ✅ Good |
| Unit tests | 26 | ✅ |
| Integration tests | 9 | ✅ |

### Test Categories Breakdown

| Category | Tests | Coverage Area |
|----------|-------|---------------|
| RetryConfig | 7 | Dataclass validation |
| Backoff Calculation | 8 | Exponential backoff logic |
| Retry Extraction | 6 | Header/message parsing |
| Synthetic Response | 3 | Error recovery |
| Integration | 2 | Config application |
| Retry Flow | 9 | End-to-end retry behavior |

---

## Future Test Priorities

1. **Agent loop testing**: Validate multi-step reasoning
2. **Tool execution testing**: Cover all built-in tools
3. **Conversation management**: Test history pruning
4. **Cost tracking**: Validate cost calculations
5. **Error scenarios**: More edge cases

---

## Resources

- **pytest documentation**: https://docs.pytest.org/
- **unittest.mock guide**: https://docs.python.org/3/library/unittest.mock.html
- **Coverage.py docs**: https://coverage.readthedocs.io/
- **Groqqy ARCHITECTURE.md**: Design and implementation details
- **Groqqy CONTRIBUTING.md**: Contributing guidelines

---

## Getting Help

**Test failures?**
1. Check this README for common patterns
2. Look at existing tests for similar scenarios
3. Run with `-v` and `-s` flags for more output
4. Create an issue if you find a bug

**Writing new tests?**
1. Follow existing test structure
2. Use descriptive names
3. Mock external dependencies
4. Aim for >75% coverage
5. Keep tests fast (<1s per file)

---

**Last updated**: 2026-01-02 (v2.5.0)
**Test suite maintained by**: Groqqy contributors
**Questions?**: Open an issue on GitHub

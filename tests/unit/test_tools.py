#!/usr/bin/env python3
"""
Test suite for tools.py - read_file line range support
"""

import pytest
from pathlib import Path
from groqqy.tools import read_file


@pytest.fixture
def test_file(tmp_path):
    """Create test file with known content"""
    file = tmp_path / "test.txt"
    content = "\n".join([f"line{i}" for i in range(1, 11)])
    file.write_text(content)
    return file


def test_read_full_file(test_file):
    """Read entire file (backwards compatibility)"""
    result = read_file(str(test_file))
    assert result.count('\n') == 9  # 10 lines, 9 newlines
    assert "line1" in result
    assert "line10" in result


def test_read_line_range(test_file):
    """Read specific line range"""
    result = read_file(str(test_file), start_line=2, end_line=4)
    assert result == "line2\nline3\nline4\n"


def test_read_from_line(test_file):
    """Read from line N to end"""
    result = read_file(str(test_file), start_line=8)
    assert result == "line8\nline9\nline10\n"


def test_read_to_line(test_file):
    """Read first N lines"""
    result = read_file(str(test_file), end_line=3)
    assert result == "line1\nline2\nline3\n"


def test_read_out_of_bounds(test_file):
    """Handle out-of-bounds gracefully"""
    result = read_file(str(test_file), start_line=1, end_line=1000)
    assert "line10" in result  # Should read to actual end


def test_read_nonexistent_file():
    """Graceful error for missing files"""
    result = read_file("/nonexistent/file.txt")
    assert "Error" in result or "not found" in result.lower()

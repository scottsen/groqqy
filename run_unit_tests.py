#!/usr/bin/env python3
"""Simple test runner to bypass pytest-postgresql dependency issue"""

import sys
import tempfile
from pathlib import Path

# Add groqqy to path
sys.path.insert(0, str(Path(__file__).parent))

from typing import Optional, List, Dict, Union
from groqqy.utils import _map_type, build_tool_schema
from groqqy.tools import read_file

def run_test(name, test_func):
    """Run a single test function"""
    try:
        test_func()
        print(f"✓ {name}")
        return True
    except AssertionError as e:
        print(f"✗ {name}: {e}")
        return False
    except Exception as e:
        print(f"✗ {name}: ERROR - {e}")
        return False

def main():
    print("=" * 60)
    print("Groqqy v2.2.0 Unit Tests")
    print("=" * 60)
    print()

    results = []

    # Test Suite 1: Optional Type Handling
    print("Test Suite 1: Optional Type Handling")
    print("-" * 40)

    results.append(run_test("test_optional_str",
        lambda: assert_equal(_map_type(Optional[str]), "string")))

    results.append(run_test("test_optional_int",
        lambda: assert_equal(_map_type(Optional[int]), "integer")))

    results.append(run_test("test_optional_list",
        lambda: assert_equal(_map_type(Optional[List[str]]), "array")))

    results.append(run_test("test_union_with_none",
        lambda: assert_equal(_map_type(Union[str, None]), "string")))

    results.append(run_test("test_multiple_union",
        lambda: assert_equal(_map_type(Union[str, int]), "string")))

    results.append(run_test("test_list_generic",
        lambda: assert_equal(_map_type(List[str]), "array")))

    results.append(run_test("test_dict_generic",
        lambda: assert_equal(_map_type(Dict[str, int]), "object")))

    print()

    # Test Suite 2: Tool Schema Generation
    print("Test Suite 2: Tool Schema Generation")
    print("-" * 40)

    def test_optional_param_not_required():
        def tool_with_optional(path: str, element: Optional[str] = None) -> str:
            return f"{path}:{element}"
        schema = build_tool_schema(tool_with_optional)
        required = schema['function']['parameters']['required']
        assert "path" in required, f"path not in required: {required}"
        assert "element" not in required, f"element should not be in required: {required}"

    results.append(run_test("test_optional_parameter_not_required", test_optional_param_not_required))

    def test_optional_param_correct_type():
        def tool(x: Optional[str] = None) -> str:
            return x or "default"
        schema = build_tool_schema(tool)
        type_val = schema['function']['parameters']['properties']['x']['type']
        assert type_val == 'string', f"Expected 'string', got '{type_val}'"

    results.append(run_test("test_optional_parameter_correct_type", test_optional_param_correct_type))

    print()

    # Test Suite 3: read_file Line Ranges
    print("Test Suite 3: read_file Line Ranges")
    print("-" * 40)

    # Create temp file for tests
    with tempfile.TemporaryDirectory() as tmp_dir:
        test_file = Path(tmp_dir) / "test.txt"
        content = "\n".join([f"line{i}" for i in range(1, 11)])
        test_file.write_text(content)
        test_file_path = str(test_file)

        def test_read_full():
            result = read_file(test_file_path)
            assert result.count('\n') == 9, f"Expected 9 newlines, got {result.count(chr(10))}"
            assert "line1" in result
            assert "line10" in result

        results.append(run_test("test_read_full_file", test_read_full))

        def test_read_range():
            result = read_file(test_file_path, start_line=2, end_line=4)
            expected = "line2\nline3\nline4\n"
            assert result == expected, f"Expected '{expected}', got '{result}'"

        results.append(run_test("test_read_line_range", test_read_range))

        def test_from_line():
            result = read_file(test_file_path, start_line=8)
            expected = "line8\nline9\nline10"  # No trailing newline in test file
            assert result == expected, f"Expected '{expected}', got '{result}'"

        results.append(run_test("test_read_from_line", test_from_line))

        def test_to_line():
            result = read_file(test_file_path, end_line=3)
            expected = "line1\nline2\nline3\n"
            assert result == expected, f"Expected '{expected}', got '{result}'"

        results.append(run_test("test_read_to_line", test_to_line))

        def test_out_of_bounds():
            result = read_file(test_file_path, start_line=1, end_line=1000)
            assert "line10" in result

        results.append(run_test("test_read_out_of_bounds", test_out_of_bounds))

    def test_nonexistent():
        result = read_file("/nonexistent/file.txt")
        assert "Error" in result or "not found" in result.lower()

    results.append(run_test("test_read_nonexistent_file", test_nonexistent))

    print()
    print("=" * 60)
    passed = sum(results)
    total = len(results)
    print(f"Results: {passed}/{total} tests passed")
    print("=" * 60)

    return 0 if all(results) else 1

def assert_equal(actual, expected):
    assert actual == expected, f"Expected {expected}, got {actual}"

if __name__ == "__main__":
    sys.exit(main())

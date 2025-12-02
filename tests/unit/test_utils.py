#!/usr/bin/env python3
"""
Test suite for utils.py - Optional type handling and schema generation
"""

import pytest
from typing import Optional, List, Dict, Union
from groqqy.utils import _map_type, build_tool_schema


def test_optional_str():
    """Optional[str] should map to 'string'"""
    assert _map_type(Optional[str]) == "string"


def test_optional_int():
    """Optional[int] should map to 'integer'"""
    assert _map_type(Optional[int]) == "integer"


def test_optional_list():
    """Optional[List[str]] should map to 'array'"""
    assert _map_type(Optional[List[str]]) == "array"


def test_union_with_none():
    """Union[str, None] should map to 'string'"""
    assert _map_type(Union[str, None]) == "string"


def test_multiple_union():
    """Union[str, int] (non-optional) should fallback to 'string'"""
    assert _map_type(Union[str, int]) == "string"


def test_list_generic():
    """List[str] should map to 'array'"""
    assert _map_type(List[str]) == "array"


def test_dict_generic():
    """Dict[str, Any] should map to 'object'"""
    assert _map_type(Dict[str, int]) == "object"


def test_optional_parameter_not_required():
    """Optional parameters should not be in required list"""
    def tool_with_optional(path: str, element: Optional[str] = None) -> str:
        return f"{path}:{element}"

    schema = build_tool_schema(tool_with_optional)
    assert "path" in schema['function']['parameters']['required']
    assert "element" not in schema['function']['parameters']['required']


def test_optional_parameter_correct_type():
    """Optional[T] should generate correct type schema"""
    def tool(x: Optional[str] = None) -> str:
        return x or "default"

    schema = build_tool_schema(tool)
    assert schema['function']['parameters']['properties']['x']['type'] == 'string'

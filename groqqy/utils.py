"""
Pure utility functions - no I/O, no side effects
Transformations only: Python objects → JSON schemas
"""

import inspect
from typing import Callable, Dict, Any


def build_tool_schema(tool: Callable) -> Dict[str, Any]:
    """
    Transform Python function → OpenAI tool schema.
    Pure transformation - no side effects.
    """
    sig = inspect.signature(tool)
    parameters = _build_parameters(sig, tool)

    return {
        "type": "function",
        "function": {
            "name": tool.__name__,
            "description": tool.__doc__ or f"{tool.__name__} function",
            "parameters": parameters
        }
    }


def _build_parameters(sig: inspect.Signature, tool: Callable) -> Dict[str, Any]:
    """Build parameter schema from signature."""
    properties = {}
    required = []

    for param_name, param in sig.parameters.items():
        properties[param_name] = _param_to_schema(param)
        if _is_required(param):
            required.append(param_name)

    return {
        "type": "object",
        "properties": properties,
        "required": required
    }


def _param_to_schema(param: inspect.Parameter) -> Dict[str, str]:
    """Convert parameter to JSON schema property."""
    param_type = _map_type(param.annotation)
    return {
        "type": param_type,
        "description": f"{param.name} parameter"
    }


def _is_required(param: inspect.Parameter) -> bool:
    """Check if parameter is required (no default)."""
    return param.default == inspect.Parameter.empty


def _map_type(annotation) -> str:
    """Map Python type to JSON schema type."""
    if annotation == inspect.Parameter.empty:
        return "string"

    type_map = {
        str: "string",
        int: "integer",
        float: "number",
        bool: "boolean",
        list: "array",
        dict: "object"
    }

    return type_map.get(annotation, "string")

from mcp import types
from .primitives import get_primitive_tools
from .modifiers import get_modifier_tools
from .transforms import get_transform_tools
from .selection import get_selection_tools
from .operators import get_operator_tools
from .architectural import get_architectural_tools


def get_modeling_tools() -> list[types.Tool]:
    """Returns all modeling-related tools"""
    tools = []
    tools.extend(get_primitive_tools())
    tools.extend(get_modifier_tools())
    tools.extend(get_transform_tools())
    tools.extend(get_selection_tools())
    tools.extend(get_operator_tools())
    tools.extend(get_architectural_tools())
    return tools

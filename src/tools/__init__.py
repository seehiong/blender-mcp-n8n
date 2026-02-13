from mcp import types
from .modeling import get_modeling_tools
from .scene import get_scene_tools
from .collections import get_collection_tools
from .materials import get_material_tools
from .lighting import get_lighting_tools
from .camera import get_camera_tools
from .animation import get_animation_tools
from .rendering import get_rendering_tools


def get_mcp_tools() -> list[types.Tool]:
    """Returns all Blender tools from all modules"""
    tools = []
    tools.extend(get_scene_tools())
    tools.extend(get_collection_tools())
    tools.extend(get_modeling_tools())
    tools.extend(get_material_tools())
    tools.extend(get_lighting_tools())
    tools.extend(get_camera_tools())
    tools.extend(get_animation_tools())
    tools.extend(get_rendering_tools())
    return tools

from mcp import types


def get_scene_tools() -> list[types.Tool]:
    return [
        types.Tool(
            name="get_scene_info",
            description="Get information about the current Blender scene",
            inputSchema={"type": "object", "properties": {}},
        ),
        types.Tool(
            name="get_object_info",
            description="Get detailed information about a specific object",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "Object name"}
                },
                "required": ["name"],
            },
        ),
        types.Tool(
            name="get_distance",
            description="Measure the distance between two objects.",
            inputSchema={
                "type": "object",
                "properties": {
                    "object_a": {"type": "string"},
                    "object_b": {"type": "string"},
                    "mode": {
                        "type": "string",
                        "enum": ["CENTER", "VERTICAL", "HORIZONTAL"],
                        "default": "CENTER",
                    },
                },
                "required": ["object_a", "object_b"],
            },
        ),
        # Diagnostics
        types.Tool(
            name="get_viewport_screenshot",
            description="Capture a screenshot of the 3D viewport.",
            inputSchema={
                "type": "object",
                "properties": {
                    "max_size": {"type": "integer", "default": 800},
                },
            },
        ),
        types.Tool(
            name="get_debug_info",
            description="Get diagnostic information about the server.",
            inputSchema={"type": "object", "properties": {}},
        ),
    ]

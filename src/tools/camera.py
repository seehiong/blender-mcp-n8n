from mcp import types


def get_camera_tools() -> list[types.Tool]:
    return [
        types.Tool(
            name="create_camera",
            description="Create camera",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "location": {"type": "array", "items": {"type": "number"}},
                    "rotation": {"type": "array", "items": {"type": "number"}},
                },
                "required": ["name", "location"],
            },
        ),
        types.Tool(
            name="set_active_camera",
            description="Set the active camera for the scene.",
            inputSchema={
                "type": "object",
                "properties": {
                    "camera_name": {"type": "string"},
                },
                "required": ["camera_name"],
            },
        ),
        types.Tool(
            name="camera_look_at",
            description="Point a camera at a target location.",
            inputSchema={
                "type": "object",
                "properties": {
                    "camera_name": {"type": "string"},
                    "target_location": {"type": "array", "items": {"type": "number"}},
                },
                "required": ["camera_name", "target_location"],
            },
        ),
    ]

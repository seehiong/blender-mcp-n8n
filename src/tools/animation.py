from mcp import types


def get_animation_tools() -> list[types.Tool]:
    return [
        types.Tool(
            name="set_keyframe",
            description="Set a keyframe for an object property.",
            inputSchema={
                "type": "object",
                "properties": {
                    "object_name": {"type": "string"},
                    "property_path": {"type": "string"},
                    "frame": {"type": "integer"},
                    "value": {"type": "array", "items": {"type": "number"}},
                },
                "required": ["object_name", "property_path", "frame", "value"],
            },
        ),
        types.Tool(
            name="get_keyframes",
            description="Get all keyframes for an object.",
            inputSchema={
                "type": "object",
                "properties": {
                    "object_name": {"type": "string"},
                },
                "required": ["object_name"],
            },
        ),
        types.Tool(
            name="set_timeline_range",
            description="Set the timeline range for animation.",
            inputSchema={
                "type": "object",
                "properties": {
                    "start_frame": {"type": "integer"},
                    "end_frame": {"type": "integer"},
                    "current_frame": {"type": "integer"},
                },
                "required": ["start_frame", "end_frame"],
            },
        ),
        types.Tool(
            name="play_animation",
            description="Play or stop animation playback.",
            inputSchema={
                "type": "object",
                "properties": {
                    "play": {"type": "boolean", "default": True},
                },
            },
        ),
    ]

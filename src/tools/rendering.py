from mcp import types


def get_rendering_tools() -> list[types.Tool]:
    return [
        types.Tool(
            name="configure_render_settings",
            description="Configure render settings.",
            inputSchema={
                "type": "object",
                "properties": {
                    "engine": {
                        "type": "string",
                        "enum": ["CYCLES", "BLENDER_EEVEE_NEXT"],
                    },
                    "samples": {"type": "integer"},
                    "resolution_x": {"type": "integer"},
                    "resolution_y": {"type": "integer"},
                },
            },
        ),
        types.Tool(
            name="render_frame",
            description="Render the current frame.",
            inputSchema={
                "type": "object",
                "properties": {
                    "output_path": {"type": "string"},
                },
            },
        ),
        types.Tool(
            name="render_animation",
            description="Render an animation sequence.",
            inputSchema={
                "type": "object",
                "properties": {
                    "start_frame": {"type": "integer"},
                    "end_frame": {"type": "integer"},
                    "output_dir": {"type": "string"},
                },
            },
        ),
    ]

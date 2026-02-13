from mcp import types


def get_lighting_tools() -> list[types.Tool]:
    return [
        types.Tool(
            name="create_light",
            description="Create light (POINT, SUN, SPOT, AREA)",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "type": {
                        "type": "string",
                        "description": "POINT, SUN, SPOT, or AREA",
                    },
                    "location": {"type": "array", "items": {"type": "number"}},
                    "energy": {"type": "number"},
                },
                "required": ["name", "type", "location"],
            },
        ),
    ]

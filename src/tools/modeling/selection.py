from mcp import types


def get_selection_tools() -> list[types.Tool]:
    return [
        types.Tool(
            name="select_objects",
            description="Select multiple objects and optionally set one as active. Deselects all other objects first.",
            inputSchema={
                "type": "object",
                "properties": {
                    "object_names": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of object names to select",
                    },
                    "active_object": {
                        "type": "string",
                        "description": "Optional name of the object to set as active",
                    },
                },
                "required": ["object_names"],
            },
        ),
        types.Tool(
            name="select_by_pattern",
            description="POWER TOOL: Select objects using a name pattern (wildcards). Perfect for selecting multiple repetitive objects like 'Facade_Fin*' or 'Window.*' in one go. Highly recommended before applying materials or transformations to groups.",
            inputSchema={
                "type": "object",
                "properties": {
                    "pattern": {
                        "type": "string",
                        "description": "Glob pattern (e.g., 'Facade_Fin*' to select all objects starting with that name)",
                    },
                    "extend": {
                        "type": "boolean",
                        "default": False,
                        "description": "If true, add to current selection instead of replacing it.",
                    },
                },
                "required": ["pattern"],
            },
        ),
    ]

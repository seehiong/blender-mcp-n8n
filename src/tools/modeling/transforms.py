from mcp import types


def get_transform_tools() -> list[types.Tool]:
    return [
        types.Tool(
            name="duplicate_object",
            description="POWER TIP: Use this tool to rename, move, and remove modifiers in ONE call! This is much faster than using multiple tools. Best for duplicating floors, slabs, or windows that need immediate placement and cleanup.",
            inputSchema={
                "type": "object",
                "properties": {
                    "object_name": {
                        "type": "string",
                        "description": "Object to duplicate",
                    },
                    "new_name": {
                        "type": "string",
                        "description": "New name for the duplicate",
                    },
                    "location": {
                        "type": "array",
                        "items": {"type": "number"},
                        "description": "Optional: New XYZ location",
                    },
                    "rotation": {
                        "type": "array",
                        "items": {"type": "number"},
                        "description": "Optional: New XYZ rotation in degrees",
                    },
                    "scale": {
                        "type": "array",
                        "items": {"type": "number"},
                        "description": "Optional: New XYZ scale",
                    },
                    "collection": {
                        "type": "string",
                        "description": "Optional: Move the duplicate to this collection",
                    },
                    "remove_modifiers": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Optional: List of modifier names to remove",
                    },
                    "linked": {
                        "type": "boolean",
                        "description": "Create linked duplicate (shares data)",
                    },
                    "hide_viewport": {
                        "type": "boolean",
                        "description": "Hide from viewport",
                    },
                    "hide_render": {
                        "type": "boolean",
                        "description": "Hide from render",
                    },
                },
                "required": ["object_name"],
            },
        ),
        types.Tool(
            name="duplicate_selection",
            description="Duplicate all currently selected objects with optional transformations. Useful for testing set_active_collection or batch duplication workflows.",
            inputSchema={
                "type": "object",
                "properties": {
                    "location_offset": {
                        "type": "array",
                        "items": {"type": "number"},
                        "description": "Optional: XYZ offset to apply to all duplicates",
                    },
                    "rotation_offset": {
                        "type": "array",
                        "items": {"type": "number"},
                        "description": "Optional: XYZ rotation offset in degrees",
                    },
                    "scale": {
                        "type": "array",
                        "items": {"type": "number"},
                        "description": "Optional: XYZ scale for duplicates",
                    },
                    "collection": {
                        "type": "string",
                        "description": "Optional: Move duplicates to this collection",
                    },
                    "remove_modifiers": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Optional: List of modifier names to remove from duplicates",
                    },
                },
            },
        ),
        types.Tool(
            name="transform_object",
            description="Transform an existing object's position, rotation, or scale.",
            inputSchema={
                "type": "object",
                "properties": {
                    "object_name": {
                        "type": "string",
                        "description": "Name of the object to transform",
                    },
                    "location": {
                        "type": "array",
                        "items": {"type": "number"},
                        "description": "Absolute XYZ position",
                    },
                    "rotation": {
                        "type": "array",
                        "items": {"type": "number"},
                        "description": "XYZ rotation in degrees",
                    },
                    "scale": {
                        "type": "array",
                        "items": {"type": "number"},
                        "description": "Absolute XYZ scale.",
                    },
                    "hide_viewport": {
                        "type": "boolean",
                        "description": "Hide from viewport",
                    },
                    "hide_render": {
                        "type": "boolean",
                        "description": "Hide from render",
                    },
                },
                "required": ["object_name"],
            },
        ),
        types.Tool(
            name="set_object_dimensions",
            description="Set exact dimensions for an object in meters.",
            inputSchema={
                "type": "object",
                "properties": {
                    "object_name": {"type": "string"},
                    "x": {"type": "number"},
                    "y": {"type": "number"},
                    "z": {"type": "number"},
                },
                "required": ["object_name", "x", "y", "z"],
            },
        ),
        types.Tool(
            name="batch_transform",
            description="Transform multiple existing objects with different positions/rotations/scales.",
            inputSchema={
                "type": "object",
                "properties": {
                    "transforms": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "object_name": {"type": "string"},
                                "location": {
                                    "type": "array",
                                    "items": {"type": "number"},
                                },
                                "rotation": {
                                    "type": "array",
                                    "items": {"type": "number"},
                                },
                                "scale": {"type": "array", "items": {"type": "number"}},
                            },
                            "required": ["object_name"],
                        },
                    },
                },
                "required": ["transforms"],
            },
        ),
    ]

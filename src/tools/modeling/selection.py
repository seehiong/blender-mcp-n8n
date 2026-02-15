from mcp import types


def get_selection_tools() -> list[types.Tool]:
    return [
        types.Tool(
            name="select_objects",
            description="[WORKFLOW WARNING] Avoid using this for sequential 'Select -> Assign' workflows as it increases API turns and hits rate limits. Many tools (like 'create_material') now accept object names directly.",
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
            description="[WORKFLOW WARNING] Avoid using this for sequential 'Select -> Assign' workflows. Instead, use the 'pattern' parameter directly in tools like 'create_material', 'assign_material', or 'batch_transform' to complete the task in ONE TURN and avoid rate limits.",
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

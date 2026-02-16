from mcp import types


def get_collection_tools() -> list[types.Tool]:
    return [
        types.Tool(
            name="create_collection",
            description="Create a new collection in the scene",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "Collection name"},
                    "parent_collection": {
                        "type": "string",
                        "description": "Optional parent collection name",
                    },
                },
                "required": ["name"],
            },
        ),
        types.Tool(
            name="set_active_collection",
            description="Set the active collection for new objects",
            inputSchema={
                "type": "object",
                "properties": {
                    "collection_name": {
                        "type": "string",
                        "description": "Collection name to make active",
                    }
                },
                "required": ["collection_name"],
            },
        ),
        types.Tool(
            name="move_to_collection",
            description="Move objects to a collection",
            inputSchema={
                "type": "object",
                "properties": {
                    "object_names": {"type": "array", "items": {"type": "string"}},
                    "collection_name": {"type": "string"},
                },
                "required": ["object_names", "collection_name"],
            },
        ),
        types.Tool(
            name="get_collections",
            description="Get hierarchy of all collections in the scene",
            inputSchema={"type": "object", "properties": {}},
        ),
        types.Tool(
            name="remove_collection",
            description="Remove a collection and optionally its contents.",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "Specific collection to remove",
                    },
                    "pattern": {
                        "type": "string",
                        "description": "Glob pattern for bulk removal (e.g. 'Test_*')",
                    },
                    "delete_objects": {
                        "type": "boolean",
                        "description": "Whether to also delete objects inside the collection(s)",
                        "default": True,
                    },
                },
            },
        ),
    ]

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
    ]

from mcp import types


def get_history_tools() -> list[types.Tool]:
    return [
        types.Tool(
            name="undo",
            description="Undo the last action in Blender",
            inputSchema={"type": "object", "properties": {}},
        ),
        types.Tool(
            name="redo",
            description="Redo the last undone action in Blender",
            inputSchema={"type": "object", "properties": {}},
        ),
    ]

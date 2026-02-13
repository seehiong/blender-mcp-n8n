import copy


def sanitize_schema(schema: dict) -> dict:
    """
    Remove default values from schema for n8n compatibility.
    n8n's MCP client doesn't handle 'default' in some environments well.
    """
    clean = copy.deepcopy(schema)
    if "properties" in clean:
        for prop in clean["properties"].values():
            if "default" in prop:
                del prop["default"]
    return clean

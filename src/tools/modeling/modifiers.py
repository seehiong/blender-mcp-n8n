from mcp import types


def get_modifier_tools() -> list[types.Tool]:
    return [
        types.Tool(
            name="apply_modifier",
            description="POWER TIP: Use 'target_objects' to add AND sync this modifier to multiple objects in ONE call! This is much faster than adding modifiers one-by-one or using copy_modifier.",
            inputSchema={
                "type": "object",
                "properties": {
                    "object_name": {
                        "type": "string",
                        "description": "Primary object to add modifier to",
                    },
                    "modifier_type": {
                        "type": "string",
                        "description": "ARRAY, SOLIDIFY, BEVEL, MIRROR, SUBSURF, etc.",
                    },
                    "name": {
                        "type": "string",
                        "description": "Optional custom name for the modifier",
                    },
                    "target_objects": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of additional object names to sync this modifier to.",
                    },
                    "count": {
                        "type": "integer",
                        "description": "For ARRAY: number of copies",
                    },
                    "use_relative_offset": {
                        "type": "boolean",
                        "description": "For ARRAY",
                    },
                    "use_constant_offset": {
                        "type": "boolean",
                        "description": "For ARRAY",
                    },
                    "constant_offset_displace": {
                        "type": "array",
                        "items": {"type": "number"},
                        "description": "For ARRAY: XYZ offset",
                    },
                    "thickness": {"type": "number", "description": "For SOLIDIFY"},
                    "offset": {"type": "number", "description": "For SOLIDIFY"},
                    "width": {"type": "number", "description": "For BEVEL"},
                    "segments": {"type": "integer", "description": "For BEVEL"},
                    "use_clamp_overlap": {
                        "type": "boolean",
                        "description": "For BEVEL",
                    },
                    "levels": {"type": "integer", "description": "For SUBSURF"},
                    "render_levels": {"type": "integer", "description": "For SUBSURF"},
                },
                "required": ["object_name", "modifier_type"],
            },
        ),
        types.Tool(
            name="remove_modifier",
            description="Remove a modifier from an object",
            inputSchema={
                "type": "object",
                "properties": {
                    "object_name": {
                        "type": "string",
                        "description": "Name of the object to remove modifier from",
                    },
                    "modifier_name": {
                        "type": "string",
                        "description": "Name of the modifier to remove",
                    },
                },
                "required": ["object_name", "modifier_name"],
            },
        ),
        types.Tool(
            name="copy_modifier",
            description="Copy a modifier from a source object to target objects.",
            inputSchema={
                "type": "object",
                "properties": {
                    "source_object": {
                        "type": "string",
                        "description": "Name of the object that has the modifier",
                    },
                    "target_objects": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of object names to copy to",
                    },
                    "modifier_name": {
                        "type": "string",
                        "description": "Exact name of the modifier to copy.",
                    },
                },
                "required": ["source_object", "target_objects", "modifier_name"],
            },
        ),
        types.Tool(
            name="boolean_operation",
            description="""Perform a boolean operation between objects or collections. 
GUIDANCE:
- Use 'SLICE' to cut a hole AND keep the resulting piece as a new object.
- Use operand_type='COLLECTION' to use all objects in a collection as cutters at once.
- CRITICAL: object_a must NOT be in collection object_b. Submitting an object's own collection as a cutter will result in self-subtraction (object disappearing).
- 'EXACT' solver is recommended for most operations.
- The cutter is automatically hidden from viewport and render by default.""",
            inputSchema={
                "type": "object",
                "properties": {
                    "object_a": {"type": "string", "description": "Base object name"},
                    "object_b": {
                        "type": "string",
                        "description": "Operand name (Object or Collection name)",
                    },
                    "operation": {
                        "type": "string",
                        "enum": ["INTERSECT", "UNION", "DIFFERENCE", "SLICE"],
                        "description": "Operation type. SLICE is custom: Difference + Intersection result.",
                    },
                    "operand_type": {
                        "type": "string",
                        "enum": ["OBJECT", "COLLECTION"],
                        "default": "OBJECT",
                        "description": "Whether object_b is a single object or a collection of objects.",
                    },
                    "solver": {
                        "type": "string",
                        "enum": ["FLOAT", "EXACT", "MANIFOLD"],
                        "default": "EXACT",
                        "description": "Solver algorithm: FLOAT (legacy/fast), EXACT (reliable), MANIFOLD (mesh-safe)",
                    },
                    "hide_cutter": {
                        "type": "boolean",
                        "default": True,
                        "description": "Hide the cutter object after operation",
                    },
                },
                "required": ["object_a", "object_b", "operation"],
            },
        ),
    ]

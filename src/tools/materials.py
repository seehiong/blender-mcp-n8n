from mcp import types


def get_material_tools() -> list[types.Tool]:
    return [
        types.Tool(
            name="create_material",
            description="Create a new material with Principled BSDF shader.",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "preset": {
                        "type": "string",
                        "enum": [
                            "glass",
                            "glass_tinted",
                            "glass_frosted",
                            "metal_brushed",
                            "metal_polished",
                            "metal_gold",
                            "metal_copper",
                            "plastic_glossy",
                            "plastic_matte",
                            "concrete",
                            "wood",
                            "rubber",
                            "emission",
                        ],
                    },
                    "base_color": {
                        "type": "string",
                        "description": "Hex color like #FF0000",
                    },
                    "roughness": {"type": "number"},
                    "metallic": {"type": "number"},
                    "transmission": {"type": "number"},
                    "ior": {"type": "number"},
                    "emission_color": {"type": "string"},
                    "emission_strength": {"type": "number"},
                    "alpha": {"type": "number"},
                    "object_names": {"type": "array", "items": {"type": "string"}},
                    "slot_index": {"type": "integer", "default": 0},
                },
                "required": ["name"],
            },
        ),
        types.Tool(
            name="assign_material",
            description="Assign an existing material to one or more objects. TIP: If 'object_names' is omitted, it applies to ALL currently selected objects. Best used after 'select_by_pattern' to handle many objects at once.",
            inputSchema={
                "type": "object",
                "properties": {
                    "object_names": {"type": "array", "items": {"type": "string"}},
                    "material_name": {"type": "string"},
                },
                "required": ["material_name"],
            },
        ),
        types.Tool(
            name="set_material_properties",
            description="Modify properties of an existing material.",
            inputSchema={
                "type": "object",
                "properties": {
                    "material_name": {"type": "string"},
                    "base_color": {"type": "string"},
                    "metallic": {"type": "number"},
                    "roughness": {"type": "number"},
                    "emission_color": {"type": "string"},
                    "emission_strength": {"type": "number"},
                    "alpha": {"type": "number"},
                    "transmission": {"type": "number"},
                },
                "required": ["material_name"],
            },
        ),
        types.Tool(
            name="add_shader_node",
            description="Add a shader node to a material's node tree.",
            inputSchema={
                "type": "object",
                "properties": {
                    "material_name": {"type": "string"},
                    "node_type": {"type": "string"},
                    "location": {"type": "array", "items": {"type": "number"}},
                },
                "required": ["material_name", "node_type", "location"],
            },
        ),
        types.Tool(
            name="connect_shader_nodes",
            description="Connect two shader nodes.",
            inputSchema={
                "type": "object",
                "properties": {
                    "material_name": {"type": "string"},
                    "from_node": {"type": "string"},
                    "from_socket": {"type": "string"},
                    "to_node": {"type": "string"},
                    "to_socket": {"type": "string"},
                },
                "required": [
                    "material_name",
                    "from_node",
                    "from_socket",
                    "to_node",
                    "to_socket",
                ],
            },
        ),
        types.Tool(
            name="assign_builtin_texture",
            description="Apply a Blender built-in procedural texture to a material.",
            inputSchema={
                "type": "object",
                "properties": {
                    "material_name": {"type": "string"},
                    "texture_type": {"type": "string"},
                },
                "required": ["material_name", "texture_type"],
            },
        ),
    ]

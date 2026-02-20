from mcp import types


def get_architectural_tools() -> list[types.Tool]:
    return [
        types.Tool(
            name="build_room_shell",
            description=(
                "PRIMARY TOOL for building a 3D architectural shell from a 2D floor plan. "
                "Use this for the ENTIRE BUILDING OUTER PERIMETER (one call). "
                "Caller supplies explicit [x,y] vertex positions in order around the perimeter. "
                "Creates three separate named objects: {name}_Floor, {name}_Walls, {name}_Ceiling. "
                "PRO TIP: After this call, use build_wall_segment and build_wall_with_door "
                "to add interior partition walls. Do NOT call this per room — call it once for the whole building."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "vertices": {
                        "type": "array",
                        "items": {
                            "type": "array",
                            "items": {"type": "number"},
                            "description": "[x, y] or [x, y, z] — z is ignored, floor is always at Z=0",
                        },
                        "description": (
                            "Ordered perimeter vertices of the building/unit footprint. "
                            "E.g. for a 10x6 rectangle: [[0,0],[10,0],[10,6],[0,6]]"
                        ),
                    },
                    "height": {
                        "type": "number",
                        "default": 2.8,
                        "description": "Ceiling/wall height in metres (default 2.8)",
                    },
                    "wall_thickness": {
                        "type": "number",
                        "default": 0.2,
                        "description": "Exterior wall thickness in metres (default 0.2 = 200mm standard).",
                    },
                    "floor_thickness": {
                        "type": "number",
                        "default": 0.15,
                        "description": "Floor slab thickness in metres, grows downward (default 0.15 = 150mm).",
                    },
                    "name": {
                        "type": "string",
                        "description": "Base name — objects will be {name}_Floor, {name}_Walls, {name}_Ceiling",
                    },
                    "collection": {
                        "type": "string",
                        "description": "Collection to place the three objects in",
                    },
                    "doors": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "edge_index": {
                                    "type": "integer",
                                    "description": "0-indexed index of the edge in the vertices loop",
                                },
                                "offset": {
                                    "type": "number",
                                    "description": "Distance from the start vertex of the edge",
                                },
                                "width": {
                                    "type": "number",
                                    "default": 0.9,
                                    "description": "Width of the door opening",
                                },
                                "height": {
                                    "type": "number",
                                    "default": 2.1,
                                    "description": "Height of the door opening",
                                },
                            },
                            "required": ["edge_index", "offset"],
                        },
                        "description": "List of door openings to cut into the exterior walls",
                    },
                    "windows": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "edge_index": {
                                    "type": "integer",
                                    "description": "0-indexed index of the edge in the vertices loop",
                                },
                                "offset": {
                                    "type": "number",
                                    "description": "Distance from the start vertex of the edge",
                                },
                                "width": {
                                    "type": "number",
                                    "default": 1.2,
                                    "description": "Width of the window opening",
                                },
                                "height": {
                                    "type": "number",
                                    "default": 1.5,
                                    "description": "Height of the window opening",
                                },
                                "sill_height": {
                                    "type": "number",
                                    "default": 0.9,
                                    "description": "Height from floor to bottom of window",
                                },
                            },
                            "required": ["edge_index", "offset"],
                        },
                        "description": "List of window openings to cut into the exterior walls",
                    },
                },
                "required": ["vertices"],
            },
        ),
        types.Tool(
            name="build_wall_segment",
            description=(
                "Create a plain interior partition wall (single flat quad face, no door). "
                "Use for solid dividers between rooms that share no opening. "
                "The wall is a zero-thickness surface from floor (Z=0) to ceiling height. "
                "WORKFLOW: build_room_shell (outer shell) → build_wall_segment (solid partitions) "
                "→ build_wall_with_door (partitions with openings)."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "start_point": {
                        "type": "array",
                        "items": {"type": "number"},
                        "description": "[x, y] or [x, y, z] start of wall base (Z forced to 0)",
                    },
                    "end_point": {
                        "type": "array",
                        "items": {"type": "number"},
                        "description": "[x, y] or [x, y, z] end of wall base (Z forced to 0)",
                    },
                    "height": {
                        "type": "number",
                        "default": 2.8,
                        "description": "Wall height in metres",
                    },
                    "thickness": {
                        "type": "number",
                        "default": 0.15,
                        "description": "Wall thickness in metres (default 0.15 = 150mm standard interior partition).",
                    },
                    "name": {"type": "string", "description": "Object name"},
                    "collection": {
                        "type": "string",
                        "description": "Collection to place object in",
                    },
                },
                "required": ["start_point", "end_point"],
            },
        ),
        types.Tool(
            name="build_wall_with_door",
            description=(
                "Create an interior wall segment with a door opening — pure vertex/face construction, no booleans. "
                "The wall is built from 3 faces: left panel (full height), lintel above door, right panel (full height). "
                "The door aperture is absent geometry (open space). "
                "Door is centred by default; pass door_offset to place it off-centre."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "start_point": {
                        "type": "array",
                        "items": {"type": "number"},
                        "description": "[x, y] or [x, y, z] start of wall base (Z forced to 0)",
                    },
                    "end_point": {
                        "type": "array",
                        "items": {"type": "number"},
                        "description": "[x, y] or [x, y, z] end of wall base (Z forced to 0)",
                    },
                    "height": {
                        "type": "number",
                        "default": 2.8,
                        "description": "Total wall height in metres",
                    },
                    "thickness": {
                        "type": "number",
                        "default": 0.15,
                        "description": "Wall thickness in metres (default 0.15 = 150mm standard interior partition).",
                    },
                    "door_offset": {
                        "type": "number",
                        "description": "Distance from start_point to left edge of door. Omit to centre.",
                    },
                    "door_width": {
                        "type": "number",
                        "default": 0.9,
                        "description": "Door opening width in metres",
                    },
                    "door_height": {
                        "type": "number",
                        "default": 2.1,
                        "description": "Door opening height in metres",
                    },
                    "name": {"type": "string", "description": "Object name"},
                    "collection": {
                        "type": "string",
                        "description": "Collection to place object in",
                    },
                },
                "required": ["start_point", "end_point"],
            },
        ),
        types.Tool(
            name="toggle_ceiling",
            description=(
                "Show or hide a ceiling (or any) object by name. "
                "Use visible=false to look inside the building shell."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "object_name": {
                        "type": "string",
                        "description": "Name of the object to toggle (e.g. 'Apartment_Ceiling')",
                    },
                    "visible": {
                        "type": "boolean",
                        "description": "true = show, false = hide",
                    },
                },
                "required": ["object_name", "visible"],
            },
        ),
        types.Tool(
            name="set_view",
            description="Switch viewport view (TOP, ISO, FRONT, SIDE). Use TOP for drawing floor plans, ISO to inspect the 3D result.",
            inputSchema={
                "type": "object",
                "properties": {
                    "mode": {
                        "type": "string",
                        "enum": ["TOP", "ISO", "FRONT", "SIDE"],
                        "default": "TOP",
                        "description": "View mode to switch to",
                    },
                },
            },
        ),
        types.Tool(
            name="build_column",
            description=(
                "Create a structural column at a specific location. "
                "Can optionally be merged (union) with a target object (e.g. Room_Walls) "
                "to ensure seamless geometry without internal overlapping faces."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "location": {
                        "type": "array",
                        "items": {"type": "number"},
                        "description": "[x, y] coordinates of the column's bottom-left corner.",
                    },
                    "width": {
                        "type": "number",
                        "default": 0.4,
                        "description": "Column width (X-dimension).",
                    },
                    "depth": {
                        "type": "number",
                        "default": 0.4,
                        "description": "Column depth (Y-dimension).",
                    },
                    "height": {
                        "type": "number",
                        "default": 2.8,
                        "description": "Column height (default 2.8m).",
                    },
                    "name": {
                        "type": "string",
                        "description": "Object name (default 'Column')",
                    },
                    "collection": {
                        "type": "string",
                        "description": "Target collection",
                    },
                    "union_with": {
                        "type": "string",
                        "description": "Optional: Name of object to merge with (e.g. 'Room_Walls').",
                    },
                },
                "required": ["location"],
            },
        ),
    ]

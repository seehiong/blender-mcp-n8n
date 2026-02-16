from mcp import types


def get_operator_tools() -> list[types.Tool]:
    return [
        types.Tool(
            name="circular_array",
            description="Create objects arranged in a circular/radial pattern (ring, circle, around a point).",
            inputSchema={
                "type": "object",
                "properties": {
                    "object_name": {
                        "type": "string",
                        "description": "Name of the object to duplicate",
                    },
                    "count": {
                        "type": "integer",
                        "description": "Total number of objects in the final array",
                    },
                    "radius": {"type": "number", "description": "Radius of the circle"},
                    "center": {
                        "type": "array",
                        "items": {"type": "number"},
                        "description": "XYZ center of the circle",
                    },
                    "start_angle": {
                        "type": "number",
                        "description": "Starting angle in degrees",
                    },
                    "axis": {
                        "type": "string",
                        "description": "Axis of rotation (X, Y, or Z)",
                        "enum": ["X", "Y", "Z"],
                    },
                    "use_radial_rotation": {
                        "type": "boolean",
                        "description": "Face the center of the ring",
                        "default": True,
                    },
                },
                "required": ["object_name", "count", "radius"],
            },
        ),
        types.Tool(
            name="join_objects",
            description="POWER TIP: Use this after 'select_by_pattern' to merge many repetitive objects into one! If 'object_names' is omitted, it joins all currently selected objects. Highly recommended for cleaning up fins, windows, or structural repetitive elements.",
            inputSchema={
                "type": "object",
                "properties": {
                    "object_names": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Optional: List of object names to join. If omitted, joins current selection.",
                    },
                    "active_object": {
                        "type": "string",
                        "description": "Optional: Object that will receive the mesh of others.",
                    },
                    "new_name": {
                        "type": "string",
                        "description": "Optional: New name for the joined object",
                    },
                },
            },
        ),
        types.Tool(
            name="create_and_array",
            description="Create a primitive with a linear array modifier.",
            inputSchema={
                "type": "object",
                "properties": {
                    "primitive_type": {
                        "type": "string",
                        "description": "cube, cylinder, sphere, or torus",
                    },
                    "location": {
                        "type": "array",
                        "items": {"type": "number"},
                        "description": "XYZ position",
                    },
                    "name": {"type": "string", "description": "Object name"},
                    "array_count": {
                        "type": "integer",
                        "description": "Number of copies",
                    },
                    "array_offset": {
                        "type": "array",
                        "items": {"type": "number"},
                        "description": "XYZ offset between copies",
                    },
                    "scale": {
                        "type": "array",
                        "items": {"type": "number"},
                        "description": "XYZ scale",
                    },
                    "rotation": {
                        "type": "array",
                        "items": {"type": "number"},
                        "description": "XYZ rotation in degrees",
                    },
                    "radius": {"type": "number"},
                    "depth": {"type": "number"},
                    "vertices": {"type": "integer"},
                    "major_radius": {"type": "number"},
                    "minor_radius": {"type": "number"},
                    "major_segments": {"type": "integer"},
                    "minor_segments": {"type": "integer"},
                },
                "required": ["primitive_type", "location"],
            },
        ),
        types.Tool(
            name="random_distribute",
            description="Randomly distribute copies of an object within a ring or volume. PRO TIP: Distribution occurs around the 'center' parameter or the source object's location if center is omitted (not necessarily the world origin).",
            inputSchema={
                "type": "object",
                "properties": {
                    "object_name": {"type": "string"},
                    "count": {"type": "integer"},
                    "min_distance": {"type": "number"},
                    "max_distance": {"type": "number"},
                    "center": {
                        "type": "array",
                        "items": {"type": "number"},
                        "description": "Optional: XYZ center of distribution. Defaults to object location.",
                    },
                    "z_position": {"type": "number", "default": 0.0},
                    "seed": {"type": "integer"},
                },
                "required": ["object_name", "count", "min_distance", "max_distance"],
            },
        ),
        types.Tool(
            name="extrude_mesh",
            description="Extrude mesh geometry (vertices, edges, or faces). PRO TIP: Use 'filter_normal' (e.g. [0,0,1] for top) to extrude specific parts of an object instead of the whole thing.",
            inputSchema={
                "type": "object",
                "properties": {
                    "object_name": {
                        "type": "string",
                        "description": "Object to extrude",
                    },
                    "mode": {
                        "type": "string",
                        "enum": ["VERTS", "EDGES", "FACES"],
                        "default": "FACES",
                        "description": "Selection mode for extrusion",
                    },
                    "move": {
                        "type": "array",
                        "items": {"type": "number"},
                        "description": "XYZ translation after extrusion",
                    },
                    "filter_normal": {
                        "type": "array",
                        "items": {"type": "number"},
                        "description": "Optional: Only extrude faces pointing in this direction (XYZ normal)",
                    },
                    "angle_threshold": {
                        "type": "number",
                        "default": 1.0,
                        "description": "Angle threshold in degrees for normal filtering",
                    },
                },
                "required": ["object_name"],
            },
        ),
        types.Tool(
            name="inset_faces",
            description="Inset faces of a mesh (great for creating walls from floors). PRO TIP: Use 'filter_normal' to only inset specific faces (like the top face).",
            inputSchema={
                "type": "object",
                "properties": {
                    "object_name": {"type": "string", "description": "Object to inset"},
                    "thickness": {"type": "number", "description": "Inset amount"},
                    "depth": {
                        "type": "number",
                        "description": "Optional extrude depth",
                    },
                    "filter_normal": {
                        "type": "array",
                        "items": {"type": "number"},
                        "description": "Optional: Only inset faces pointing in this direction (XYZ normal)",
                    },
                    "angle_threshold": {
                        "type": "number",
                        "default": 1.0,
                        "description": "Angle threshold in degrees for normal filtering",
                    },
                },
                "required": ["object_name", "thickness"],
            },
        ),
        types.Tool(
            name="shear_mesh",
            description="Shear mesh geometry along an axis (useful for sloped roofs). PRO TIP: Use 'filter_normal' (e.g. [0,0,1]) to shear only the top faces.",
            inputSchema={
                "type": "object",
                "properties": {
                    "object_name": {"type": "string"},
                    "value": {"type": "number", "description": "Shear factor"},
                    "axis": {
                        "type": "string",
                        "enum": ["X", "Y", "Z"],
                        "description": "Axis to shear along (View axis)",
                    },
                    "orient_axis": {
                        "type": "string",
                        "enum": ["X", "Y", "Z"],
                        "description": "Axis orthogonal to the shear plane",
                    },
                    "filter_normal": {
                        "type": "array",
                        "items": {"type": "number"},
                        "description": "Optional: Only shear faces pointing in this direction (XYZ normal)",
                    },
                    "angle_threshold": {
                        "type": "number",
                        "default": 1.0,
                        "description": "Angle threshold in degrees for normal filtering",
                    },
                },
                "required": ["object_name", "value"],
            },
        ),
        types.Tool(
            name="delete_object",
            description="Delete object(s) by name or pattern (e.g. 'Test_*').",
            inputSchema={
                "type": "object",
                "properties": {
                    "object_name": {
                        "type": "string",
                        "description": "Specific object to delete",
                    },
                    "pattern": {
                        "type": "string",
                        "description": "Glob pattern for bulk deletion (e.g. 'Test_*')",
                    },
                },
            },
        ),
    ]

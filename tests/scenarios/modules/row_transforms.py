from tests.utils.mcp_client import MCPClient


def create_transforms_row(client: MCPClient, y_offset: float = 40.0):
    print(f"Creating Transforms Row at Y={y_offset}...")

    # 1. Duplicate Object (x=0)
    # Testing renaming, moving, and removing modifiers in one call
    client.call_tool(
        "create_cube",
        {
            "size": 2.0,
            "location": [0, y_offset, 0.0],
            "name": "Transform_Source_Cube",
        },
    )
    client.call_tool(
        "apply_modifier",
        {
            "modifier_type": "WIREFRAME",
            "name": "WireToRemove",
            "object_name": "Transform_Source_Cube",
            "thickness": 0.1,
        },
    )
    # Duplicate and modify: rename, move to y=y_offset+3, remove wireframe, show in render AND viewport
    client.call_tool(
        "duplicate_object",
        {
            "object_name": "Transform_Source_Cube",
            "new_name": "Transform_Dup_Cube",
            "location": [0.0, y_offset + 3.0, 0.0],
            "remove_modifiers": ["WireToRemove"],
            "hide_render": False,
            "hide_viewport": False,
        },
    )

    # 2. Transform Object (x=5)
    client.call_tool(
        "create_cube",
        {"size": 1.0, "location": [5.0, y_offset, 0.0], "name": "Transform_Move_Cube"},
    )
    client.call_tool(
        "transform_object",
        {
            "object_name": "Transform_Move_Cube",
            "location": [5.0, y_offset, 2.0],
            "rotation": [45.0, 0.0, 45.0],
            "scale": [2.0, 0.5, 1.0],
        },
    )

    # 3. Set Object Dimensions (x=10)
    client.call_tool(
        "create_cube",
        {"size": 1.0, "location": [10.0, y_offset, 0.0], "name": "Transform_Dim_Cube"},
    )
    client.call_tool(
        "set_object_dimensions",
        {
            "object_name": "Transform_Dim_Cube",
            "x": 3.0,
            "y": 1.0,
            "z": 0.5,
        },
    )

    # 4. Batch Transform (x=15)
    # Create two spheres to transform
    client.call_tool(
        "create_sphere",
        {"radius": 0.5, "location": [15.0, y_offset, 0.0], "name": "Transform_Batch_1"},
    )
    client.call_tool(
        "create_sphere",
        {"radius": 0.5, "location": [17.0, y_offset, 0.0], "name": "Transform_Batch_2"},
    )
    client.call_tool(
        "batch_transform",
        {
            "transforms": [
                {
                    "object_name": "Transform_Batch_1",
                    "location": [15.0, y_offset + 2.0, 2.0],
                    "scale": [2.0, 2.0, 2.0],
                },
                {
                    "object_name": "Transform_Batch_2",
                    "location": [15.0, y_offset + 2.0, -2.0],
                    "rotation": [0.0, 90.0, 0.0],
                },
            ]
        },
    )

    # 5. Duplicate Selection (x=20)
    # Select Batch_1 and Batch_2 then duplicate with offset
    # Fixed tool name: select_objects
    client.call_tool(
        "select_objects", {"object_names": ["Transform_Batch_1", "Transform_Batch_2"]}
    )

    client.call_tool(
        "duplicate_selection",
        {
            "location_offset": [5.0, 0.0, 0.0],
            "rotation_offset": [0.0, 0.0, 45.0],
            "scale": [0.5, 0.5, 0.5],
        },
    )

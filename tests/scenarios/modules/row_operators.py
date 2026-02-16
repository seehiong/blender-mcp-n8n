from tests.utils.mcp_client import MCPClient


def test_circular_array(client: MCPClient, x_start: float, y: float):
    print("Testing circular_array...")
    client.call_tool(
        "create_cylinder",
        {
            "name": "Test_Op_Circ_Base",
            "radius": 0.2,
            "depth": 1.0,
            "location": [x_start, y, 0.0],
        },
    )
    client.call_tool(
        "circular_array",
        {
            "object_name": "Test_Op_Circ_Base",
            "count": 6,
            "radius": 2.0,
            "center": [x_start, y, 0.0],
        },
    )


def test_join_objects(client: MCPClient, x_start: float, y: float):
    print("Testing join_objects...")
    # Create 3 small cubes
    names = []
    for i in range(3):
        name = f"Test_Op_Join_{i}"
        client.call_tool(
            "create_cube",
            {"name": name, "size": 0.5, "location": [x_start + i * 0.7, y, 0.0]},
        )
        names.append(name)

    # Select them and join
    client.call_tool("select_by_pattern", {"pattern": "Test_Op_Join_*"})
    client.call_tool("join_objects", {"new_name": "Test_Op_Joined_Result"})


def test_create_and_array(client: MCPClient, x_start: float, y: float):
    print("Testing create_and_array...")
    client.call_tool(
        "create_and_array",
        {
            "primitive_type": "cube",
            "name": "Test_Op_CreateArray",
            "location": [x_start, y, 0.0],
            "scale": [0.5, 0.5, 0.5],
            "array_count": 5,
            "array_offset": [1.0, 0.0, 0.0],
        },
    )


def test_random_distribute(client: MCPClient, x_start: float, y: float):
    print("Testing random_distribute...")
    client.call_tool(
        "create_sphere",
        {"name": "Test_Op_Rand_Base", "radius": 0.2, "location": [x_start, y, 0.0]},
    )
    client.call_tool(
        "random_distribute",
        {
            "object_name": "Test_Op_Rand_Base",
            "count": 10,
            "min_distance": 1.0,
            "max_distance": 2.0,
            "center": [x_start, y, 0.0],
            "z_position": 0.0,
        },
    )


def test_extrude_mesh(client: MCPClient, x_start: float, y: float):
    print("Testing extrude_mesh (Directional)...")
    client.call_tool(
        "create_cylinder",
        {
            "name": "Test_Op_Extrude",
            "radius": 1.0,
            "depth": 1.0,  # Height 1.0
            "location": [x_start, y, 0.5],  # Center at Z=0.5 so base is at 0
        },
    )
    # Extrude TOP face (0,0,1) by 1.0 -> should result in a cylinder of height 2.0
    client.call_tool(
        "extrude_mesh",
        {
            "object_name": "Test_Op_Extrude",
            "filter_normal": [0.0, 0.0, 1.0],
            "move": [0.0, 0.0, 1.0],
        },
    )


def test_inset_faces(client: MCPClient, x_start: float, y: float):
    print("Testing inset_faces (Directional)...")
    client.call_tool(
        "create_cube",
        {"name": "Test_Op_Inset", "size": 1.0, "location": [x_start, y, 0.5]},
    )
    # Inset TOP face (0,0,1) and push it DOWN
    client.call_tool(
        "inset_faces",
        {
            "object_name": "Test_Op_Inset",
            "filter_normal": [0.0, 0.0, 1.0],
            "thickness": 0.2,
            "depth": -0.3,
        },
    )


def test_shear_mesh(client: MCPClient, x_start: float, y: float):
    print("Testing shear_mesh (Cylinder Lean)...")
    client.call_tool(
        "create_cylinder",
        {
            "name": "Test_Op_Shear_Cylinder",
            "radius": 0.5,
            "depth": 3.0,
            "location": [x_start, y, 1.5],
        },
    )
    # Shear TOP face along Y axis to create 45-degree lean
    client.call_tool(
        "shear_mesh",
        {
            "object_name": "Test_Op_Shear_Cylinder",
            "filter_normal": [0.0, 0.0, 1.0],
            "value": 1.5,
            "axis": "Y",
            "orient_axis": "Z",
        },
    )


def test_delete_object(client: MCPClient, x_start: float, y: float):
    print("Testing delete_object (Pattern Deletion)...")

    # Create torus (should survive)
    client.call_tool(
        "create_torus",
        {
            "name": "Test_Op_Delete_Torus_Survivor",
            "major_radius": 0.5,
            "minor_radius": 0.2,
            "location": [x_start, y, 0],
        },
    )

    # Create cylinder
    client.call_tool(
        "create_cylinder",
        {
            "name": "Test_Op_Delete_Cylinder_Survivor",
            "radius": 0.3,
            "depth": 1.0,
            "location": [x_start + 2.0, y, 0],
        },
    )

    # Create cubes to be deleted (pattern: Test_Op_Delete_Cube_*)
    client.call_tool(
        "create_cube",
        {
            "name": "Test_Op_Delete_Cube_1",
            "size": 0.5,
            "location": [x_start, y + 3.0, 0],
        },
    )
    client.call_tool(
        "create_cube",
        {
            "name": "Test_Op_Delete_Cube_2",
            "dimensions": [0.5, 1.5, 0.5],
            "location": [x_start + 2.0, y + 3.0, 0],
        },
    )

    # Delete the cylinder specifically (it won't be a survivor anymore!)
    client.call_tool(
        "delete_object", {"object_name": "Test_Op_Delete_Cylinder_Survivor"}
    )

    # Delete all remaining Cube pattern objects
    client.call_tool("delete_object", {"pattern": "Test_Op_Delete_Cube_*"})

    # Result: Only Torus should remain standing


def create_operators_row(client: MCPClient, y_offset: float = 30.0):
    print(f"Creating Operators Row at Y={y_offset}...")

    test_circular_array(client, 0.0, y_offset)
    test_join_objects(client, 5.0, y_offset)
    test_create_and_array(client, 10.0, y_offset)
    test_random_distribute(client, 15.0, y_offset)
    test_extrude_mesh(client, 20.0, y_offset)
    test_inset_faces(client, 25.0, y_offset)
    test_shear_mesh(client, 30.0, y_offset)
    test_delete_object(client, 35.0, y_offset)

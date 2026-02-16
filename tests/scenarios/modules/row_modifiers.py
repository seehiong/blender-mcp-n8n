from tests.utils.mcp_client import MCPClient


def create_modifiers_row(client: MCPClient, y_offset: float = 10.0):
    print(f"Creating Modifiers Row at Y={y_offset}...")

    # 1. Apply Modifiers (Static Props)
    test_apply_modifiers(client, y_offset)

    # 2. Copy/Remove Modifiers
    test_copy_remove_modifiers(client, y_offset)

    # 3. Boolean Operations (High-level)
    test_boolean_ops(client, y_offset)


def test_apply_modifiers(client: MCPClient, y_offset: float):
    print(
        "Running Apply Modifiers tests (Array, Solidify, Bevel, Mirror, Subdiv, Wire, Smooth)..."
    )

    # Array (x=0)
    client.call_tool(
        "create_cube",
        {"size": 0.5, "location": [0.0, y_offset, 0.0], "name": "Test_Mod_Array"},
    )
    client.call_tool(
        "apply_modifier",
        {
            "modifier_type": "ARRAY",
            "name": "TestArray",
            "object_name": "Test_Mod_Array",
            "count": 3,
            "use_relative_offset": True,
            "relative_offset_displace": [1.5, 0.0, 0.0],
        },
    )

    # Solidify (x=5)
    client.call_tool(
        "create_plane",
        {"size": 2.0, "location": [5.0, y_offset, 0.0], "name": "Test_Mod_Solidify"},
    )
    client.call_tool(
        "apply_modifier",
        {
            "modifier_type": "SOLIDIFY",
            "name": "TestSolidify",
            "object_name": "Test_Mod_Solidify",
            "thickness": 0.3,
        },
    )

    # Bevel (x=10)
    client.call_tool(
        "create_cube",
        {"size": 2.0, "location": [10.0, y_offset, 0.0], "name": "Test_Mod_Bevel"},
    )
    client.call_tool(
        "apply_modifier",
        {
            "modifier_type": "BEVEL",
            "name": "TestBevel",
            "object_name": "Test_Mod_Bevel",
            "width": 0.2,
            "segments": 3,
        },
    )

    # Mirror (x=15)
    client.call_tool(
        "create_cube",
        {
            "size": 0.1,
            "location": [15.0, y_offset + 2.5, 0.0],
            "name": "Test_MirrorCenter_Y",
        },
    )
    client.call_tool(
        "create_cube",
        {"size": 0.5, "location": [15.0, y_offset, 0.0], "name": "Test_Mod_Mirror"},
    )
    client.call_tool(
        "apply_modifier",
        {
            "modifier_type": "MIRROR",
            "name": "TestMirror",
            "object_name": "Test_Mod_Mirror",
            "use_axis": [False, True, False],
            "mirror_object": "Test_MirrorCenter_Y",
        },
    )

    # Subdiv (x=20)
    client.call_tool(
        "create_cube",
        {"size": 2.0, "location": [20.0, y_offset, 0.0], "name": "Test_Mod_Subdiv"},
    )
    client.call_tool(
        "apply_modifier",
        {
            "modifier_type": "SUBSURF",
            "name": "TestSubsurf",
            "object_name": "Test_Mod_Subdiv",
            "levels": 2,
        },
    )

    # Wireframe (x=25)
    client.call_tool(
        "create_cube",
        {"size": 2.0, "location": [25.0, y_offset, 0.0], "name": "Test_Mod_Wire"},
    )
    client.call_tool(
        "apply_modifier",
        {
            "modifier_type": "WIREFRAME",
            "name": "TestWire",
            "object_name": "Test_Mod_Wire",
            "thickness": 0.05,
        },
    )

    # Smooth (x=30)
    client.call_tool(
        "create_sphere",
        {"radius": 1.0, "location": [30.0, y_offset, 0.0], "name": "Test_Mod_Smooth"},
    )
    client.call_tool(
        "apply_modifier",
        {
            "modifier_type": "SMOOTH",
            "name": "TestSmooth",
            "object_name": "Test_Mod_Smooth",
            "factor": 1.0,
            "iterations": 10,
        },
    )

    # Basic Boolean Modifier (x=35) - To distinguish from high-level tool
    # Use a Cylinder as cutter for a distinct visual difference
    client.call_tool(
        "create_cube",
        {
            "size": 2.0,
            "location": [35.0, y_offset, 0.0],
            "name": "Test_Mod_BoolBasic_Base",
        },
    )
    client.call_tool(
        "create_cylinder",
        {
            "radius": 0.7,
            "depth": 3.0,
            "location": [35.0, y_offset, 0.0],
            "name": "Test_Mod_BoolBasic_Cutter",
        },
    )
    client.call_tool(
        "apply_modifier",
        {
            "modifier_type": "BOOLEAN",
            "name": "TestBoolBasic",
            "object_name": "Test_Mod_BoolBasic_Base",
            "object_b": "Test_Mod_BoolBasic_Cutter",
            "operation": "DIFFERENCE",
            "hide_cutter": True,
        },
    )


def test_copy_remove_modifiers(client: MCPClient, y_offset: float):
    print("Running Modifier Removal tests (Copy/Remove at x=40)...")

    # 1. Create a Collection for the targets
    collection_name = "Collection_CopyRemove"
    client.call_tool("create_collection", {"name": collection_name})

    # 2. Create Target cubes at x=40
    # Cube 1 at x=40, y_offset
    client.call_tool(
        "create_cube",
        {
            "size": 1.0,
            "location": [40.0, y_offset, 0.0],
            "name": "Test_Mod_RemoveVerify_1",
            "collection": collection_name,
        },
    )
    # Cube 2 at x=40, y_offset+5
    client.call_tool(
        "create_cube",
        {
            "size": 1.0,
            "location": [40.0, y_offset + 5.0, 0.0],
            "name": "Test_Mod_RemoveVerify_2",
            "collection": collection_name,
        },
    )

    # 3. Copy 'TestWire' from Source (x=25) to Target Collection
    client.call_tool(
        "copy_modifier",
        {
            "source_object": "Test_Mod_Wire",
            "target_collection": collection_name,
            "modifier_name": "TestWire",
        },
    )

    # 4. Remove from Target 2 specifically
    # Result: Cube 1 (y_offset) still has Wireframe, Cube 2 (y_offset+5) is now Solid
    client.call_tool(
        "remove_modifier",
        {"object_name": "Test_Mod_RemoveVerify_2", "modifier_name": "TestWire"},
    )


def test_boolean_ops(client: MCPClient, y_offset: float):
    print(
        "Running Boolean Operations tests (Intersect, Union, Difference, Slice starting at x=45)..."
    )

    # helper to create pair
    def create_pair(x, name):
        client.call_tool(
            "create_cube",
            {"size": 2.0, "location": [x, y_offset, 0.0], "name": f"{name}_Base"},
        )
        client.call_tool(
            "create_sphere",
            {"radius": 1.2, "location": [x, y_offset, 1.0], "name": f"{name}_Cutter"},
        )
        return f"{name}_Base", f"{name}_Cutter"

    # Intersect (x=45)
    b, c = create_pair(45, "Test_BoolOp_Intersect")
    client.call_tool(
        "boolean_operation", {"object_a": b, "object_b": c, "operation": "INTERSECT"}
    )

    # Union (x=50)
    b, c = create_pair(50, "Test_BoolOp_Union")
    client.call_tool(
        "boolean_operation", {"object_a": b, "object_b": c, "operation": "UNION"}
    )

    # Difference (x=55)
    b, c = create_pair(55, "Test_BoolOp_Diff")
    client.call_tool(
        "boolean_operation", {"object_a": b, "object_b": c, "operation": "DIFFERENCE"}
    )

    # Slice (x=60)
    # We'll slice a Sphere with an elongated Cube for a clear result
    client.call_tool(
        "create_sphere",
        {
            "radius": 1.5,
            "location": [60.0, y_offset, 0.0],
            "name": "Test_BoolOp_Slice_Base",
        },
    )
    client.call_tool(
        "create_cube",
        {
            "size": 1.0,
            "scale": [3.0, 0.2, 3.0],  # Elongated sheet
            "location": [60.0, y_offset, 0.0],
            "name": "Test_BoolOp_Slice_Cutter",
        },
    )

    client.call_tool(
        "boolean_operation",
        {
            "object_a": "Test_BoolOp_Slice_Base",
            "object_b": "Test_BoolOp_Slice_Cutter",
            "operation": "SLICE",
            "hide_cutter": True,
        },
    )

    # Resulting slice piece is 'Test_BoolOp_Slice_Base_slice'
    client.call_tool(
        "transform_object",
        {
            "object_name": "Test_BoolOp_Slice_Base_slice",
            "location": [60.0, y_offset, 2.5],  # Offset to see both pieces
            "hide_viewport": False,
        },
    )

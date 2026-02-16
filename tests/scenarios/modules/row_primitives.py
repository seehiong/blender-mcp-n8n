from tests.utils.mcp_client import MCPClient


def create_primitives_row(client: MCPClient, y_offset: float = 0.0):
    """Creates a row of primitive objects at the specified Y offset."""
    print(f"Creating Primitives Row at Y={y_offset}...")

    primitives = [
        ("create_cube", {"size": 2.0}, "Cube"),
        ("create_cylinder", {"radius": 1.0, "depth": 2.0}, "Cylinder"),
        ("create_icosphere", {"radius": 1.0}, "IcoSphere"),
        ("create_sphere", {"radius": 1.0}, "Sphere"),
        ("create_torus", {"major_radius": 1.0, "minor_radius": 0.25}, "Torus"),
        ("create_plane", {"size": 2.0}, "Plane"),
    ]

    for i, (tool, args, name_suffix) in enumerate(primitives):
        x = i * 5.0
        args["location"] = [x, y_offset, 0.0]
        args["name"] = f"Test_Primitive_{name_suffix}"
        print(f"Creating {args['name']} at {args['location']}")
        client.call_tool(tool, args)

import click
import json
import sys
from pathlib import Path
from tests.utils.mcp_client import MCPClient
from tests.utils.stateful_mcp_client import StatefulMCPClient
from tests.scenarios.grid_layout import GridLayoutScenario

# Configure paths
TESTS_DIR = Path(__file__).parent
BENCHMARKS_DIR = TESTS_DIR / "benchmarks"
BENCHMARK_FILE = BENCHMARKS_DIR / "expected_scene.json"
LAST_RUN_FILE = BENCHMARKS_DIR / "last_run.json"


@click.group()
def cli():
    """Blender MCP Integration Test Runner"""
    pass


@cli.command()
@click.option("--host", default="http://localhost:8000", help="MCP Server URL")
@click.option("--verify", is_flag=True, help="Verify against benchmark after running")
@click.option(
    "--module",
    type=click.Choice(
        ["primitives", "modifiers", "collections", "operators", "transforms"]
    ),
    help="Run specific row/module",
)
@click.option(
    "--transport",
    type=click.Choice(["stateless", "stateful"]),
    default="stateful",
    help="Transport mode to use",
)
def run(host, verify, module, transport):
    """Run the integration test scenario"""
    if transport == "stateful":
        print(f"Connecting to {host} in STATEFUL mode...")
        client = StatefulMCPClient(base_url=host)
    else:
        print(f"Connecting to {host} in STATELESS mode...")
        client = MCPClient(base_url=host)

    # 1. Clear Scene (Optional but recommended)
    print("Clearing scene of test objects...")
    cleanup_patterns = [
        "Test_*",
        "Test_Integration_Collection*",
        "Collection_CopyRemove*",
        "MirrorCenter*",
        "Transform_*",
        "Text*",
        "Label_*",
    ]
    for pattern in cleanup_patterns:
        try:
            client.call_tool("delete_object", {"pattern": pattern})
        except Exception as e:
            print(f"Cleanup failed for pattern {pattern}: {e}")

    # 2. Run Scenario
    scenario = GridLayoutScenario(client)
    scenario.run(module=module)

    # 3. Snapshot
    print("Capturing scene state...")
    scene_info = client.call_tool("get_scene_info", {})

    # Get details for created objects
    detailed_objects = {}
    if "objects" in scene_info and isinstance(scene_info["objects"], list):
        for obj in scene_info["objects"]:
            name = obj.get("name")
            if name and (
                name.startswith("Test_") or name == "Test_Integration_Collection"
            ):
                # Fetch detailed info for test objects
                details = client.call_tool("get_object_info", {"name": name})
                detailed_objects[name] = details

    snapshot = {"scene_summary": scene_info, "detailed_objects": detailed_objects}

    # Ensure benchmarks dir exists
    BENCHMARKS_DIR.mkdir(exist_ok=True)

    with open(LAST_RUN_FILE, "w") as f:
        json.dump(snapshot, f, indent=2)
    print(f"Snapshot saved to {LAST_RUN_FILE}")

    if verify:
        verify_results()


@cli.command()
def verify():
    """Verify the last run against the benchmark"""
    verify_results()


def verify_results():
    if not BENCHMARK_FILE.exists():
        print(
            f"No benchmark file found at {BENCHMARK_FILE}. Run 'approve' to bless the last run."
        )
        return

    if not LAST_RUN_FILE.exists():
        print(f"No last run file found at {LAST_RUN_FILE}. Run 'run' first.")
        return

    with open(BENCHMARK_FILE, "r") as f:
        expected = json.load(f)

    with open(LAST_RUN_FILE, "r") as f:
        actual = json.load(f)

    # Simple comparison for now - can be expanded to be more robust (ignoring dynamic IDs etc)
    # For a start, let's verify object counts and existence of key testing objects

    print("Verifying Results...")
    exit_code = 0

    # Check 1: Object Existence
    expected_objs = set(expected.get("detailed_objects", {}).keys())
    actual_objs = set(actual.get("detailed_objects", {}).keys())

    missing = expected_objs - actual_objs
    unexpected = actual_objs - expected_objs

    if missing:
        print(f"❌ Missing objects: {missing}")
        exit_code = 1

    if unexpected:
        print(f"⚠️ Unexpected objects: {unexpected}")

    if not missing:
        print("✅ All expected test objects found.")

    # Check 2: Basic Property Matching (Location)
    for name in expected_objs.intersection(actual_objs):
        if name.startswith("Test_Op_Rand_Base"):
            continue

        exp_data = expected["detailed_objects"][name]
        act_data = actual["detailed_objects"][name]

        # Check Location
        if "location" in exp_data and "location" in act_data:
            # simple fuzzy match
            exp_loc = [float(x) for x in exp_data["location"]]
            act_loc = [float(x) for x in act_data["location"]]

            if not all(abs(a - b) < 0.01 for a, b in zip(exp_loc, act_loc)):
                print(
                    f"❌ Location mismatch for {name}: Expected {exp_loc}, Got {act_loc}"
                )
                exit_code = 1

    if exit_code == 0:
        print("✅ Verification Passed!")
    else:
        print("❌ Verification Failed.")
        sys.exit(exit_code)


@cli.command()
def approve():
    """Approve the last run as the new benchmark"""
    if not LAST_RUN_FILE.exists():
        print("No last run to approve.")
        return

    import shutil

    shutil.copy(LAST_RUN_FILE, BENCHMARK_FILE)
    print(f"Benchmark updated at {BENCHMARK_FILE}")


if __name__ == "__main__":
    cli()

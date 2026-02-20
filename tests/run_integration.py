import click
import json
import sys
import os
from pathlib import Path

# Add project root to sys.path to allow running as a script
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tests.utils.mcp_client import MCPClient
from tests.utils.stateful_mcp_client import StatefulMCPClient
from tests.scenarios.grid_layout import GridLayoutScenario
from tests.scenarios.arch_layout import ArchLayoutScenario

# Configure paths
TESTS_DIR = Path(__file__).parent
BENCHMARKS_DIR = TESTS_DIR / "benchmarks"

SCENARIOS = {
    "grid": GridLayoutScenario,
    "arch": ArchLayoutScenario,
}


@click.group()
def cli():
    """Blender MCP Integration Test Runner"""
    pass


@cli.command()
@click.option("--host", default="http://localhost:8000", help="MCP Server URL")
@click.option("--verify", is_flag=True, help="Verify against benchmark after running")
@click.option(
    "--scenario",
    "-s",
    type=click.Choice(["grid", "arch", "all"]),
    default="all",
    help="Scenario to run (default: all)",
)
@click.option(
    "--module",
    type=click.Choice(
        ["primitives", "modifiers", "collections", "operators", "transforms"]
    ),
    help="Run specific row/module (Grid only)",
)
@click.option(
    "--transport",
    type=click.Choice(["stateless", "stateful"]),
    default="stateful",
    help="Transport mode to use",
)
def run(host, verify, scenario, module, transport):
    """Run the integration test scenario(s)"""
    scenarios_to_run = [scenario] if scenario != "all" else list(SCENARIOS.keys())

    if transport == "stateless":
        print(f"Connecting to {host} in STATELESS mode...")
        client = MCPClient(base_url=host)
    else:
        print(f"Connecting to {host} in STATEFUL mode...")
        client = StatefulMCPClient(base_url=host)

    for s_name in scenarios_to_run:
        print(f"\n--- Running Scenario: {s_name} ---")
        benchmark_file = BENCHMARKS_DIR / f"{s_name}_expected.json"
        last_run_file = BENCHMARKS_DIR / f"{s_name}_last_run.json"

        # 1. Clear Scene
        print("Clearing scene...")
        try:
            client.call_tool("delete_object", {"pattern": "*"})
        except Exception as e:
            print(f"Cleanup failed: {e}")

        # 2. Run Scenario
        scenario_class = SCENARIOS[s_name]
        s_inst = scenario_class(client)
        if s_name == "grid":
            s_inst.run(module=module)
        else:
            s_inst.run()

        # 3. Snapshot
        print("Capturing scene state...")
        scene_info = client.call_tool("get_scene_info", {})

        # Get details for created objects
        detailed_objects = {}
        if "objects" in scene_info and isinstance(scene_info["objects"], list):
            for obj in scene_info["objects"]:
                name = obj.get("name")
                if not name:
                    continue

                # Identify test objects
                is_test_obj = (
                    name.startswith("Test_")
                    or name.startswith("HDB_")
                    or name.startswith("Wall_")
                    or name.startswith("Col_")
                    or name.startswith("Lbl_")
                    or name.startswith("Unit_")
                    or name == "Test_Integration_Collection"
                )

                if is_test_obj:
                    details = client.call_tool("get_object_info", {"name": name})
                    detailed_objects[name] = details

        snapshot = {"scene_summary": scene_info, "detailed_objects": detailed_objects}
        BENCHMARKS_DIR.mkdir(exist_ok=True)

        with open(last_run_file, "w") as f:
            json.dump(snapshot, f, indent=2)
        print(f"Snapshot saved to {last_run_file}")

        if verify:
            verify_results(benchmark_file, last_run_file)


@cli.command()
@click.option(
    "--scenario",
    "-s",
    type=click.Choice(["grid", "arch", "all"]),
    default="all",
    help="Scenario to verify",
)
def verify(scenario):
    """Verify the last run(s) against the benchmark(s)"""
    scenarios_to_verify = [scenario] if scenario != "all" else list(SCENARIOS.keys())
    for s_name in scenarios_to_verify:
        benchmark_file = BENCHMARKS_DIR / f"{s_name}_expected.json"
        last_run_file = BENCHMARKS_DIR / f"{s_name}_last_run.json"
        verify_results(benchmark_file, last_run_file)


def verify_results(benchmark_file, last_run_file):
    if not benchmark_file.exists():
        print(f"No benchmark file found at {benchmark_file}. Run 'approve' to bless.")
        return

    if not last_run_file.exists():
        print(f"No last run found at {last_run_file}.")
        return

    with open(benchmark_file, "r") as f:
        expected = json.load(f)
    with open(last_run_file, "r") as f:
        actual = json.load(f)

    print(f"Verifying {last_run_file.name} against {benchmark_file.name}...")
    exit_code = 0

    def fuzzy_match(a, b, tol=0.01):
        if isinstance(a, (list, tuple)):
            if len(a) != len(b):
                return False
            return all(fuzzy_match(x, y, tol) for x, y in zip(a, b))
        try:
            return abs(float(a) - float(b)) < tol
        except (ValueError, TypeError):
            return a == b

    # Object existence
    expected_objs = set(expected.get("detailed_objects", {}).keys())
    actual_objs = set(actual.get("detailed_objects", {}).keys())

    missing = expected_objs - actual_objs
    unexpected = actual_objs - expected_objs

    if missing:
        print(f"❌ Missing objects: {missing}")
        exit_code = 1
    if unexpected:
        print(f"❌ Unexpected objects: {unexpected}")
        exit_code = 1
    if not missing and not unexpected:
        print(f"✅ Object set matches ({len(actual_objs)} objects).")

    # Property matching
    for name in expected_objs.intersection(actual_objs):
        exp_data = expected["detailed_objects"][name]
        act_data = actual["detailed_objects"][name]
        props = [
            ("location", "Location"),
            ("rotation", "Rotation"),
            ("scale", "Scale"),
            ("dimensions", "Dimensions"),
            ("vertices", "Vertices"),
            ("faces", "Faces"),
        ]

        for p_key, p_label in props:
            if p_key in exp_data:
                if p_key not in act_data:
                    print(f"❌ Missing {p_key} for {name}")
                    exit_code = 1
                    continue
                if not fuzzy_match(exp_data[p_key], act_data[p_key]):
                    print(
                        f"❌ {p_label} mismatch for {name}: {exp_data[p_key]} vs {act_data[p_key]}"
                    )
                    exit_code = 1

    if exit_code != 0:
        sys.exit(exit_code)
    print("✅ Verification Passed!")


@cli.command()
@click.option(
    "--scenario",
    "-s",
    type=click.Choice(["grid", "arch", "all"]),
    default="all",
    help="Scenario to approve",
)
def approve(scenario):
    """Approve the last run(s) as the new benchmark(s)"""
    scenarios_to_approve = [scenario] if scenario != "all" else list(SCENARIOS.keys())
    import shutil

    for s_name in scenarios_to_approve:
        benchmark_file = BENCHMARKS_DIR / f"{s_name}_expected.json"
        last_run_file = BENCHMARKS_DIR / f"{s_name}_last_run.json"
        if last_run_file.exists():
            shutil.copy(last_run_file, benchmark_file)
            print(f"Benchmark updated at {benchmark_file}")
        else:
            print(f"No last run found for {s_name}")


if __name__ == "__main__":
    cli()


@cli.command()
@click.option(
    "--scenario",
    "-s",
    type=click.Choice(["grid", "hdb"]),
    default="grid",
    help="Scenario to approve",
)
def approve(scenario):
    """Approve the last run as the new benchmark"""
    benchmark_file = BENCHMARKS_DIR / f"{scenario}_expected.json"
    last_run_file = BENCHMARKS_DIR / f"{scenario}_last_run.json"

    if not last_run_file.exists():
        print(f"No last run found at {last_run_file} to approve.")
        return

    import shutil

    shutil.copy(last_run_file, benchmark_file)
    print(f"Benchmark updated at {benchmark_file}")


if __name__ == "__main__":
    cli()

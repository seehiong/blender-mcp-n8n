# Integration Tests

This guide explains how to run the integration test suite for the Blender MCP addon. The test suite uses a CLI tool to automate the creation of test scenes and verify the results against a benchmark.

## Prerequisites

1.  **Blender MCP Addon**: Ensure Blender is open and the addon server is started (N-Panel > Blender MCP > Start Server).
2.  **MCP Bridge Server**: Ensure the Python bridge is running (`python -m src.main`).
3.  **Dependencies**: Install the required Python packages:
    ```bash
    pip install -r requirements.txt
    ```

### Transport Modes

The test runner supports two transport modes for communicating with the MCP server:

-   **Stateless**: Uses simple HTTP POST requests with a session ID. This emulates how n8n and other stateless clients interact with the server.
-   **Stateful (Default)**: Uses the official MCP SDK to perform a standard HTTP Streamable handshake and long-running session.

```bash
# Run in stateful mode (default)
python -m tests.run_integration run --transport stateful

# Run in stateless mode
python -m tests.run_integration run --transport stateless
```

## Running Tests

The test runner is a CLI tool located at `tests/run_integration.py`.

### 1. Run Standard Test

To run the standard grid layout scenario:

```bash
python -m tests.run_integration run
```

**What this does:**

![Integration Test Result](images/integration_test_result.png)

1.  Connects to the MCP server.
2.  Generates a grid of objects in Blender:
    -   **Row 1 (Y=0, Primitives)**: Cube, Sphere, Cylinder, Torus, Plane, IcoSphere.
    -   **Row 2 (Y=10, Modifiers)**: Bevel, Array, Subdivision Surface.
    -   **Row 3 (Y=20, Collections)**: Collection hierarchies and visibility.
    -   **Row 4 (Y=30, Operators)**: Boolean operations (Union, Difference, Intersect).
    -   **Row 5 (Y=40, Transforms)**: Move, Rotate, Scale, Duplicate, Batch operations.
3.  Captures the scene state to `tests/benchmarks/last_run.json`.

### Advanced Run Options

```bash
# Run all tests
set PYTHONPATH=. && python -m tests.run_integration run

# Run specific module (faster)
set PYTHONPATH=. && python -m tests.run_integration run --module modifiers
# Options: primitives, modifiers, collections

# Verify against benchmark
set PYTHONPATH=. && python -m tests.run_integration verify
```

If the scene matches the expected state, you will see `✅ Verification Passed!`. If not, it will report missing or unexpected objects and property mismatches.

### 3. Run and Verify in One Step

You can run and verify in a single command:

```bash
python -m tests.run_integration run --verify
```

## Updating Baselines

If you make intentional changes to the test scenario or addon logic that affect the output, you can update the benchmark to reflect the new expected state:

```bash
python -m tests.run_integration approve
```

This copies `tests/benchmarks/last_run.json` to `tests/benchmarks/expected_scene.json`.

## Extending the Test Suite

### Adding New Test Modules

The test suite uses a modular "row" based approach where each category of tests is a separate module that generates a row of objects in the Blender grid.

To add a new test module (e.g., `physics`):

1.  **Create a Module File**:
    Create `tests/scenarios/modules/row_physics.py`:
    ```python
    from tests.utils.mcp_client import MCPClient

    def create_physics_row(client: MCPClient, y_offset: float):
        print(f"Creating Physics Row at Y={y_offset}...")
        # Add tool calls here...
    ```

2.  **Register in Scenario**:
    Update `tests/scenarios/grid_layout.py`:
    - Import your function: `from tests.scenarios.modules.row_physics import create_physics_row`
    - Add it to the `run()` method with a text label:
      ```python
      if not module or module == "physics":
          self.client.call_tool("create_text", {"text": "Physics", "location": [-5.0, 50.0, 0.0], ...})
          create_physics_row(self.client, y_offset=50.0)
      ```

3.  **Update CLI Runner**:
    Update `tests/run_integration.py`:
    - Add "physics" to the `type=click.Choice([...])` list for the `--module` option.

### Structure

-   `tests/run_integration.py`: CLI entry point.
-   `tests/scenarios/grid_layout.py`: Main scenario orchestrator.
-   `tests/scenarios/modules/`: Individual test logic files (one per row).
-   `tests/utils/`: shared utilities (`MCPClient`, `stateful_mcp_client`).
-   `tests/benchmarks/`: JSON snapshots of expected scene state.

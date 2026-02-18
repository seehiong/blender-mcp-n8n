# Unit Tests

This document describes the unit tests for the Blender MCP project, focusing on core logic that can be tested without a running Blender instance.

## Session Lifecycle Tests

The primary unit test suite is located at `tests/test_sessions.py`. It verifies the core recording and playback logic of the `BridgeSession` system.

### Running the Tests

To execute the session unit tests, run:

```bash
python -m tests.test_sessions
```

### Test Coverage

The `test_session_lifecycle` suite performs the following validations:

1.  **Initializing Recorder**: Creates a new `SessionRecorder` with a target JSON path and metadata.
2.  **Recording Commands**: Records mock tool calls (e.g., `create_cube`, `create_cylinder`) to ensure they are correctly captured in memory.
3.  **Verifying File Existence**: Confirms that the session is automatically saved to the filesystem after each command.
4.  **Validating JSON Structure**: Reads the generated `.json` file and verifies that the schema, metadata, and command arguments match the recorded data.
5.  **Round-trip Loading**: Tests `BridgeSession.load()` to ensure a saved session can be reloaded into a Python object without data loss.
6.  **Cleanup**: Automatically removes the temporary test file upon success.

### Example Output

Upon a successful run, you should see:

```text
1. Initializing Recorder with path: test_unit_session.json
2. Recording mock commands: 'create_cube', 'create_cylinder'...
3. Verifying file existence: test_unit_session.json
4. Validating JSON structure and data integrity...
5. Testing BridgeSession.load() round-trip...
6. Cleaning up temporary test file...
✅ Session Lifecycle Unit Test Passed!
```

---

> [!NOTE]
> These tests are "pure Python" and do not require the Blender Addon to be active. They test the Bridge logic specifically. For testing actual Blender tool execution, see [Integration Tests](integration_tests.md).

import os
import json
from src.sessions import SessionMetadata, SessionRecorder, BridgeSession


def test_session_lifecycle():
    path = "test_unit_session.json"
    print(f"1. Initializing Recorder with path: {path}")
    metadata = SessionMetadata(name="Test Session", description="Unit Test")
    recorder = SessionRecorder(path, metadata)

    print("2. Recording mock commands: 'create_cube', 'create_cylinder'...")
    recorder.record_command("create_cube", {"name": "Cube1"})
    recorder.record_command("create_cylinder", {"name": "Cyl1", "radius": 2.0})

    print(f"3. Verifying file existence: {path}")
    assert os.path.exists(path)

    print("4. Validating JSON structure and data integrity...")
    with open(path, "r") as f:
        data = json.load(f)

    assert data["metadata"]["name"] == "Test Session"
    assert len(data["commands"]) == 2
    assert data["commands"][0]["tool"] == "create_cube"
    assert data["commands"][1]["arguments"]["radius"] == 2.0

    print("5. Testing BridgeSession.load() round-trip...")
    reloaded = BridgeSession.load(path)
    assert reloaded.metadata.name == "Test Session"
    assert len(reloaded.commands) == 2

    print("6. Cleaning up temporary test file...")
    os.remove(path)
    print("✅ Session Lifecycle Unit Test Passed!")


if __name__ == "__main__":
    test_session_lifecycle()

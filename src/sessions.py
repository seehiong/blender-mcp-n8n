import json
import time
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Any, Optional
from datetime import datetime


@dataclass
class SessionMetadata:
    name: str = "Untitled Session"
    model: str = ""
    description: str = ""
    documentation_url: str = ""
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class SessionCommand:
    tool: str
    arguments: Dict[str, Any]
    description: Optional[str] = None
    timestamp: float = field(default_factory=time.time)


@dataclass
class BridgeSession:
    metadata: SessionMetadata
    commands: List[SessionCommand] = field(default_factory=list)

    def to_dict(self):
        return {
            "metadata": asdict(self.metadata),
            "commands": [asdict(cmd) for cmd in self.commands],
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]):
        metadata = SessionMetadata(**data.get("metadata", {}))
        commands = [SessionCommand(**cmd) for cmd in data.get("commands", [])]
        return cls(metadata=metadata, commands=commands)

    def save(self, path: str):
        with open(path, "w") as f:
            json.dump(self.to_dict(), f, indent=2)

    @classmethod
    def load(cls, path: str):
        with open(path, "r") as f:
            data = json.load(f)
        return cls.from_dict(data)


class SessionRecorder:
    def __init__(self, path: str, metadata: SessionMetadata):
        self.path = path
        self.session = BridgeSession(metadata=metadata)

    def record_command(
        self, tool: str, arguments: Dict[str, Any], description: str = None
    ):
        command = SessionCommand(
            tool=tool, arguments=arguments, description=description
        )
        self.session.commands.append(command)
        # Auto-save after each command to prevent data loss
        self.session.save(self.path)


class SessionPlayer:
    def __init__(
        self, transport: str = "stateful", host: str = "http://localhost:8000"
    ):
        self.transport = transport
        self.host = host
        self._client = None

    def _get_client(self):
        if self._client:
            return self._client

        if self.transport == "stateful":
            from tests.utils.stateful_mcp_client import StatefulMCPClient

            self._client = StatefulMCPClient(base_url=self.host)
        else:
            from tests.utils.mcp_client import MCPClient

            self._client = MCPClient(base_url=self.host)
        return self._client

    def play(self, session: BridgeSession):
        client = self._get_client()

        # ANSI Color codes
        green = "\033[92m"
        red = "\033[91m"
        cyan = "\033[96m"
        reset = "\033[0m"
        bold = "\033[1m"

        print(f"\n{bold}Playing session:{reset} {cyan}{session.metadata.name}{reset}")
        if session.metadata.description:
            print(f"{bold}Description:{reset} {session.metadata.description}")
        print("-" * 60)

        success_count = 0
        fail_count = 0

        for i, cmd in enumerate(session.commands):
            # Print command and header
            print(
                f"{bold}[{i + 1}/{len(session.commands)}]{reset} Calling {cyan}{cmd.tool}{reset}..."
            )

            # Print description if available
            if cmd.description:
                # Indent and prefix descriptions for readability
                indented_desc = "\n".join(
                    [f"  | {line}" for line in cmd.description.splitlines()]
                )
                print(f"{indented_desc}")

            try:
                client.call_tool(cmd.tool, cmd.arguments)
                # Success indicator
                print(f"  {bold}{green}✓ SUCCESS{reset}")
                success_count += 1
            except Exception as e:
                # Failure indicator
                print(f"  {bold}{red}✘ ERROR:{reset} {e}")
                fail_count += 1

            print("-" * 60)

        # Final Summary
        label_width = 16
        print(f"\n{bold}Playback Summary:{reset}")
        print(f"  {'Total Commands:':<{label_width}} {len(session.commands)}")
        print(f"  {green}{'Successes:':<{label_width}} {success_count}{reset}")

        fail_color = red if fail_count > 0 else green
        print(f"  {fail_color}{'Failures:':<{label_width}} {fail_count}{reset}")

        print(f"\n{bold}{green if fail_count == 0 else red}Playback finished.{reset}")

import uvicorn
import logging
import click
from .sessions import SessionRecorder, SessionMetadata, BridgeSession, SessionPlayer

# Setup logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("mcp_server")


@click.group()
def cli():
    """Blender MCP Bridge CLI"""
    pass


@cli.command()
@click.option("--host", default="0.0.0.0", help="Host to bind the server to")
@click.option("--port", default=8000, help="Port to bind the server to")
@click.option(
    "--record",
    "record_path",
    type=click.Path(),
    help="Path to record the session to (JSON)",
)
@click.option("--name", default="Recorded Session", help="Session name")
@click.option("--model", default="", help="AI model name used")
@click.option("--description", default="", help="Session description")
@click.option("--url", "doc_url", default="", help="Documentation URL")
def serve(host, port, record_path, name, model, description, doc_url):
    """Start the Blender MCP server"""
    import src.server as server_mod

    if record_path:
        metadata = SessionMetadata(
            name=name, model=model, description=description, documentation_url=doc_url
        )
        server_mod.recorder = SessionRecorder(record_path, metadata)
        print(f"RECORDER ACTIVE: Saving to {record_path}")

    print("============================================================")
    print("Starting High-Stability n8n MCP Server (Modular)")
    print(f"HTTP Streamable: http://{host}:{port}/mcp")
    print("============================================================")

    uvicorn.run(
        server_mod.app, host=host, port=port, log_level="warning", access_log=False
    )


@cli.command()
@click.argument("path", type=click.Path(exists=True))
@click.option(
    "--transport",
    type=click.Choice(["stateless", "stateful"]),
    default="stateful",
    help="Transport mode to use",
)
@click.option("--host", default="http://localhost:8000", help="Target MCP Server URL")
def play(path, transport, host):
    """Playback a recorded session JSON file"""
    print(f"Playing back session from {path}...")
    session = BridgeSession.load(path)
    player = SessionPlayer(transport=transport, host=host)
    player.play(session)


if __name__ == "__main__":
    cli()

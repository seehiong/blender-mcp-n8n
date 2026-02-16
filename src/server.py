import json
import random
import string
import os
from dotenv import load_dotenv

from mcp.server import Server
from mcp.server.streamable_http_manager import StreamableHTTPSessionManager
import mcp.types as types

from .connection import blender, logger
from .tools import get_mcp_tools

load_dotenv()

# Initialize MCP Server
app = Server("blender-mcp-n8n")

ASSETS_DIR = os.getenv("BLENDER_ASSETS_DIR")


def resolve_path(args):
    """Resolve relative paths in arguments against ASSETS_DIR"""
    if not ASSETS_DIR:
        return args

    for key in ["image_path", "filepath"]:
        if (
            key in args
            and args[key]
            and isinstance(args[key], str)
            and not os.path.isabs(args[key])
        ):
            base_path = os.path.join(ASSETS_DIR, args[key])
            resolved_path = base_path
            print(f"[DEBUG] Checking base path: {base_path}")

            # If the exact file exists, use it
            if os.path.exists(base_path):
                print(f"[DEBUG] Found exact match: {base_path}")
                resolved_path = base_path
            else:
                # Try extensions
                print("Exact match failed. Trying extensions...")
                # Split off any existing extension to try others
                root, _ = os.path.splitext(base_path)

                for ext in [".exr", ".hdr", ".png", ".jpg", ".jpeg", ".tiff", ".tga"]:
                    test_path = root + ext
                    # print(f"[DEBUG] Checking Extension: {test_path}")
                    if os.path.exists(test_path):
                        print(f"[DEBUG] Found match with extension: {test_path}")
                        resolved_path = test_path
                        break

            # Normalize path for cross-platform compatibility
            args[key] = os.path.normpath(resolved_path).replace("\\", "/")
            print(f"[DEBUG] Final resolved path: {args[key]}")
    return args


@app.list_tools()
async def list_tools() -> list[types.Tool]:
    """Expose available Blender tools to the AI Agent"""
    return get_mcp_tools()


@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[types.TextContent]:
    """Handle tool calls from the AI Agent"""
    rid = "".join(random.choices(string.ascii_uppercase + string.digits, k=6))

    # Strip n8n-specific metadata
    meta = {"sessionId", "action", "chatInput", "toolCallId", "id"}
    clean_args = {k: v for k, v in arguments.items() if k not in meta}

    # Resolve paths
    clean_args = resolve_path(clean_args)

    logger.info(f"[{rid}] Tool Call: {name} with params: {clean_args}")

    blender_res = blender.send_command(name, clean_args, rid)

    # Flatten nested results from bridge
    if (
        isinstance(blender_res, dict)
        and "result" in blender_res
        and "status" in blender_res
    ):
        status_val = blender_res["status"]
        blender_res = blender_res["result"]
        if isinstance(blender_res, dict) and "status" not in blender_res:
            blender_res["status"] = status_val

    # Add success indicator to the message
    log_status = "OK"
    if isinstance(blender_res, dict):
        if "message" in blender_res:
            pass  # Use message as is
        elif "status" in blender_res and (
            blender_res["status"] == "success" or blender_res.get("success") is True
        ):
            blender_res["message"] = f"{name} completed successfully."

        if "error" in blender_res or blender_res.get("status") == "error":
            log_status = "ERROR"

    # Mirror success indicator in local console log
    log_msg = blender_res.get("message", blender_res.get("status", "Done"))
    if "error" in blender_res:
        log_msg = f"ERROR: {blender_res['error']}"

    logger.info(f"[{rid}] [{log_status}] {log_msg}")

    return [types.TextContent(type="text", text=json.dumps(blender_res, indent=2))]


# ASGI Application (HTTP Streamable Transport)
session_manager = StreamableHTTPSessionManager(
    app=app, json_response=True, stateless=True
)

# Track lifespan state
_lifespan_context = None


async def mcp_app(scope, receive, send):
    """The main ASGI application entry point"""
    global _lifespan_context

    if scope["type"] == "lifespan":
        # Handle lifespan events to initialize session_manager
        while True:
            message = await receive()
            if message["type"] == "lifespan.startup":
                try:
                    # Start the session manager
                    _lifespan_context = session_manager.run()
                    await _lifespan_context.__aenter__()
                    await send({"type": "lifespan.startup.complete"})
                except Exception as e:
                    await send({"type": "lifespan.startup.failed", "message": str(e)})
                    raise
            elif message["type"] == "lifespan.shutdown":
                try:
                    if _lifespan_context:
                        await _lifespan_context.__aexit__(None, None, None)
                    await send({"type": "lifespan.shutdown.complete"})
                except Exception as e:
                    await send({"type": "lifespan.shutdown.failed", "message": str(e)})
                    raise
                return
    elif scope["type"] == "http" and scope["path"] == "/mcp":
        await session_manager.handle_request(scope, receive, send)
    elif scope["type"] == "http":
        # 404 for other paths
        await send({"type": "http.response.start", "status": 404, "headers": []})
        await send({"type": "http.response.body", "body": b"Not Found"})

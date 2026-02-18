import json
import random
import string
import os
from typing import Optional
from contextlib import asynccontextmanager
from dotenv import load_dotenv

from mcp.server import Server
from mcp.server.streamable_http_manager import StreamableHTTPSessionManager
import mcp.types as types

from .connection import blender, logger
from .tools import get_mcp_tools
from .sessions import SessionRecorder

from starlette.applications import Starlette
from starlette.middleware.cors import CORSMiddleware
from starlette.staticfiles import StaticFiles
from starlette.responses import Response
from starlette.routing import Route, Mount

load_dotenv()

# Lifecycle / Recording State
recorder: Optional[SessionRecorder] = None

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

    if recorder:
        recorder.record_command(name, clean_args)

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


# MCP Application Logic (Streamable Transport)
# Lines below set up the Starlette/MCP integration
session_manager = StreamableHTTPSessionManager(
    app=app, json_response=True, stateless=True
)


@asynccontextmanager
async def lifespan(app: Starlette):
    """Manage the lifecycle of the MCP session manager"""
    print("[DEBUG] Starlette lifespan starting...")
    async with session_manager.run():
        print("[DEBUG] MCP Session Manager active.")
        yield
    print("[DEBUG] Starlette lifespan shutting down...")


async def mcp_asgi(scope, receive, send):
    """Raw ASGI bridge to MCP session manager. Handles OPTIONS for CORS preflight."""
    if scope["type"] == "http" and scope.get("method") == "OPTIONS":
        # Return 200 for CORS preflight — middleware will add the headers
        await send({"type": "http.response.start", "status": 200, "headers": []})
        await send({"type": "http.response.body", "body": b""})
        return
    await session_manager.handle_request(scope, receive, send)


async def root_redirect(request):
    return Response(
        "Blender MCP Server is running. Access /editor/ for the Session Editor.",
        media_type="text/plain",
    )


# Create the Starlette app
starlette_app = Starlette(
    routes=[
        Route("/", root_redirect),
        Mount("/mcp", app=mcp_asgi),
        Mount(
            "/editor", StaticFiles(directory="session_editor", html=True), name="editor"
        ),
    ],
    lifespan=lifespan,
)

# Add CORS middleware
starlette_app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Replace the mcp_app with starlette_app for the final entry point
# Note: Keep variable name as 'app' for uvicorn compatibility in main.py
app = starlette_app

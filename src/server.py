import json
import random
import string
import os
from dotenv import load_dotenv

from mcp.server import Server
from mcp.server.sse import SseServerTransport
import mcp.types as types

from .connection import blender, logger
from .tools import get_mcp_tools
from .tools.utils import sanitize_schema

load_dotenv()

# Initialize MCP Server
app = Server("blender-mcp-n8n")

ASSETS_DIR = os.getenv("BLENDER_ASSETS_DIR")


def resolve_path(args):
    """Resolve relative paths in arguments against ASSETS_DIR"""
    if not ASSETS_DIR:
        return args

    print(f"[DEBUG] resolve_path called with args: {args}")
    print(f"[DEBUG] ASSETS_DIR: {ASSETS_DIR}")

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
                print(f"[DEBUG] Exact match failed. Trying extensions...")
                for ext in [".exr", ".hdr", ".png", ".jpg", ".jpeg", ".tiff", ".tga"]:
                    test_path = base_path + ext
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

    # Add success indicator to the message
    log_status = "OK"
    if isinstance(blender_res, dict):
        if "message" in blender_res:
            pass  # Use message as is
        elif "status" in blender_res and blender_res["status"] == "success":
            blender_res["message"] = f"{name} completed successfully."

        if "error" in blender_res or blender_res.get("status") == "error":
            log_status = "ERROR"

    # Mirror success indicator in local console log
    log_msg = blender_res.get("message", blender_res.get("status", "Done"))
    if "error" in blender_res:
        log_msg = f"ERROR: {blender_res['error']}"

    logger.info(f"[{rid}] [{log_status}] {log_msg}")

    return [types.TextContent(type="text", text=json.dumps(blender_res, indent=2))]


# ASGI Application (Stateless Fallback + SSE)
sse = SseServerTransport("/sse")


async def mcp_app(scope, receive, send):
    """The main ASGI application entry point"""
    if scope["type"] == "http":
        path = scope["path"]
        method = scope["method"]

        if path == "/sse" and method == "GET":
            async with sse.connect_sse(scope, receive, send) as (
                read_stream,
                write_stream,
            ):
                await app.run(
                    read_stream, write_stream, app.create_initialization_options()
                )

        elif path == "/sse" and method == "POST":
            # Pure Stateless Fallback for n8n/stateless clients
            body_bytes = b""
            while True:
                message = await receive()
                if message["type"] == "http.request":
                    body_bytes += message.get("body", b"")
                    if not message.get("more_body", False):
                        break

            body = json.loads(body_bytes.decode("utf-8"))
            m = body.get("method")
            rid = body.get("id")

            if m in ["initialize", "notifications/initialized", "tools/list"]:
                logger.debug(f"Stateless Lifecycle: {m}")
            else:
                logger.debug(f"Stateless Request: {m}")

            # Send 200 OK headers
            await send(
                {
                    "type": "http.response.start",
                    "status": 200,
                    "headers": [(b"content-type", b"application/json")],
                }
            )

            res = None
            if m == "initialize":
                res = {
                    "jsonrpc": "2.0",
                    "id": rid,
                    "result": {
                        "protocolVersion": "2024-11-05",
                        "capabilities": {"tools": {}},
                        "serverInfo": {"name": "blender-mcp-n8n", "version": "0.1.0"},
                    },
                }
            elif m == "notifications/initialized":
                res = None
            elif m == "tools/list":
                res = {
                    "jsonrpc": "2.0",
                    "id": rid,
                    "result": {
                        "tools": [
                            {
                                "name": t.name,
                                "description": t.description,
                                "inputSchema": sanitize_schema(t.inputSchema),
                            }
                            for t in get_mcp_tools()
                        ]
                    },
                }
            elif m == "tools/call":
                p = body.get("params", {})
                tool_name = p.get("name")
                args = p.get("arguments", {})
                call_rid = "".join(
                    random.choices(string.ascii_uppercase + string.digits, k=6)
                )

                meta = {"sessionId", "action", "chatInput", "toolCallId", "id"}
                clean_args = {k: v for k, v in args.items() if k not in meta}

                # Resolve paths
                clean_args = resolve_path(clean_args)

                logger.info(
                    f"[{call_rid}] Stateless Fallback Exec: {tool_name} with params: {clean_args}"
                )
                blender_res = blender.send_command(tool_name, clean_args, call_rid)

                log_status = "OK"
                if isinstance(blender_res, dict):
                    if "message" in blender_res:
                        pass  # Use message as is
                    elif "status" in blender_res and blender_res["status"] == "success":
                        blender_res["message"] = f"{tool_name} completed successfully."

                    if "error" in blender_res or blender_res.get("status") == "error":
                        log_status = "ERROR"

                log_msg = blender_res.get("message", blender_res.get("status", "Done"))
                if "error" in blender_res:
                    log_msg = f"ERROR: {blender_res['error']}"

                logger.info(f"[{call_rid}] [{log_status}] {log_msg}")

                res = {
                    "jsonrpc": "2.0",
                    "id": rid,
                    "result": {
                        "content": [
                            {"type": "text", "text": json.dumps(blender_res, indent=2)}
                        ],
                        "isError": "error" in blender_res,
                    },
                }

            if res:
                await send(
                    {
                        "type": "http.response.body",
                        "body": json.dumps(res).encode("utf-8"),
                    }
                )
            else:
                await send({"type": "http.response.body", "body": b""})
        else:
            # 404 for other paths
            await send({"type": "http.response.start", "status": 404, "headers": []})
            await send({"type": "http.response.body", "body": b"Not Found"})
    else:
        # Not HTTP
        pass

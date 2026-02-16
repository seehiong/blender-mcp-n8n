import asyncio
import json
import traceback
from mcp.client.session import ClientSession
from mcp.client.streamable_http import streamable_http_client


class StatefulMCPClient:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
        self.mcp_url = f"{base_url}/mcp"

    async def _call_tool_async(self, name, arguments=None):
        if arguments is None:
            arguments = {}

        async with streamable_http_client(self.mcp_url) as streams:
            if isinstance(streams, tuple):
                if len(streams) == 3:
                    read_stream, write_stream, _get_session_id = streams
                elif len(streams) == 2:
                    read_stream, write_stream = streams
                else:
                    raise ValueError(f"Unexpected stream tuple length: {len(streams)}")
            else:
                raise ValueError(f"Unexpected stream return type: {type(streams)}")

            async with ClientSession(read_stream, write_stream) as session:
                await session.initialize()
                result = await session.call_tool(name, arguments)

                # result.content is a list of content items (TextContent, ImageContent etc.)
                if result.content and hasattr(result.content[0], "text"):
                    return json.loads(result.content[0].text)
                return {"status": "success", "raw_result": str(result.content)}

    def call_tool(self, name, arguments=None):
        """Synchronous wrapper for async tool call"""
        try:
            result = asyncio.run(self._call_tool_async(name, arguments))
            print(f"  [CLIENT] {name}: {result.get('status', 'ok')}")
            return result
        except Exception as e:
            print(f"  [CLIENT ERROR] {name}: {type(e).__name__}: {e}")
            if hasattr(e, "exceptions"):
                for i, exc in enumerate(e.exceptions):
                    print(f"    Sub-exception {i + 1}: {type(exc).__name__}: {exc}")
            traceback.print_exc()
            return {"status": "error", "message": str(e)}

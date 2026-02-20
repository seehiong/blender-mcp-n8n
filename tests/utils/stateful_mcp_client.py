import asyncio
import json
import traceback
from mcp.client.session import ClientSession
from mcp.client.streamable_http import streamable_http_client


class StatefulMCPClient:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
        self.mcp_url = f"{base_url}/mcp/?transport=stateful"
        self._session = None
        self._exit_stack = None

    async def _get_session(self):
        """Internal helper to get or create a persistent session"""
        if self._session is None:
            from contextlib import AsyncExitStack

            self._exit_stack = AsyncExitStack()

            # Establish the stream and session
            streams = await self._exit_stack.enter_async_context(
                streamable_http_client(self.mcp_url)
            )

            if isinstance(streams, tuple):
                read_stream, write_stream = streams[:2]
            else:
                raise ValueError(f"Unexpected stream return type: {type(streams)}")

            session = await self._exit_stack.enter_async_context(
                ClientSession(read_stream, write_stream)
            )
            await session.initialize()
            self._session = session

        return self._session

    async def _call_tool_async(self, name, arguments=None):
        if arguments is None:
            arguments = {}

        session = await self._get_session()
        result = await session.call_tool(name, arguments)

        # result.content is a list of content items (TextContent, ImageContent etc.)
        if result.content and hasattr(result.content[0], "text"):
            return json.loads(result.content[0].text)
        return {"status": "success", "raw_result": str(result.content)}

    def call_tool(self, name, arguments=None):
        """Synchronous wrapper for async tool call"""
        try:
            # We use a persistent loop to keep the session alive if needed,
            # but for simple CLI scripts, asyncio.run works as long as the
            # object instance (self) persists and we manage the loop correctly.
            # Using a custom loop for the class instance:
            if not hasattr(self, "_loop"):
                self._loop = asyncio.new_event_loop()

            result = self._loop.run_until_complete(
                self._call_tool_async(name, arguments)
            )
            print(f"  [CLIENT] {name}: {result.get('status', 'ok')}")
            return result
        except Exception as e:
            print(f"  [CLIENT ERROR] {name}: {type(e).__name__}: {e}")
            traceback.print_exc()
            return {"status": "error", "message": str(e)}

    def __del__(self):
        """Cleanup persistent resources"""
        if hasattr(self, "_exit_stack") and self._exit_stack:
            if hasattr(self, "_loop") and self._loop.is_running():
                # Cannot easily close async stack from sync __del__ without a running loop
                pass

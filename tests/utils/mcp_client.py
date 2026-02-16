import httpx
import json
import random
import string
import traceback


class MCPClient:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
        self.mcp_url = f"{base_url}/mcp"
        self.session_id = "".join(
            random.choices(string.ascii_letters + string.digits, k=8)
        )

    def call_tool(self, name, arguments=None):
        if arguments is None:
            arguments = {}

        payload = {
            "jsonrpc": "2.0",
            "method": "tools/call",
            "id": self._generate_id(),
            "params": {
                "name": name,
                "arguments": arguments,
            },
        }

        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json, text/event-stream",
        }

        try:
            response = httpx.post(
                self.mcp_url, json=payload, headers=headers, timeout=60.0
            )
            response.raise_for_status()
            data = response.json()

            # The server wraps the result in a specific JSON-RPC format
            # We need to extract the actual content
            if "result" in data and "content" in data["result"]:
                content_list = data["result"]["content"]
                if content_list and content_list[0]["type"] == "text":
                    # The text field contains a stringified JSON of the tool result
                    tool_result_str = content_list[0]["text"]
                    result = json.loads(tool_result_str)
                    print(f"  [CLIENT] {name}: {result.get('status', 'ok')}")
                    return result

            print(f"  [CLIENT] {name}: raw response")
            return data
        except Exception as e:
            print(f"  [CLIENT ERROR] {name}: {e}")
            traceback.print_exc()
            return {
                "status": "error",
                "message": str(e),
                "data": str(response.text if "response" in locals() else ""),
            }

    def _generate_id(self):
        return "".join(random.choices(string.ascii_letters + string.digits, k=6))

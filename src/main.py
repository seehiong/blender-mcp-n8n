import uvicorn
import logging
from .server import mcp_app

# Setup logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("mcp_server")


def main():
    """Start the Blender MCP server using uvicorn"""
    print("============================================================")
    print("Starting High-Stability N8N MCP Server (Modular)")
    print("SSE: http://localhost:8000/sse")
    print("============================================================")

    uvicorn.run(mcp_app, host="0.0.0.0", port=8000, log_level="info", access_log=False)


if __name__ == "__main__":
    main()

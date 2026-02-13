import os
import socket
import json
import logging
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()


@dataclass
class Config:
    blender_host: str = os.getenv("BLENDER_MCP_HOST", "127.0.0.1")
    blender_port: int = int(os.getenv("BLENDER_MCP_PORT", "9877"))


config = Config()
logger = logging.getLogger("mcp_server")


class BlenderConnection:
    """Handles socket communication with the Blender addon"""

    def recv_all(self, sock):
        """Helper to receive all data from professional socket connection"""
        data = b""
        while True:
            try:
                chunk = sock.recv(4096)
                if not chunk:
                    break
                data += chunk
                if len(chunk) < 4096:
                    break
            except socket.timeout:
                sock.settimeout(0.5)
                continue
            except Exception:
                break
        return data

    def send_command(self, command_type, params=None, rid="unknown"):
        """Sends a JSON-RPC style command to Blender via TCP socket"""
        clean_params = params if params else {}

        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5.0)  # High stability timeout
            sock.connect((config.blender_host, config.blender_port))

            payload = {"type": command_type, "params": clean_params, "request_id": rid}
            sock.sendall(json.dumps(payload).encode("utf-8"))

            response_data = self.recv_all(sock)
            if not response_data:
                return {"status": "error", "message": "No response from Blender"}

            return json.loads(response_data.decode("utf-8"))
        except Exception as e:
            logger.error(f"Blender Connection Error: {e}")
            return {"status": "error", "message": str(e)}
        finally:
            sock.close()


blender = BlenderConnection()

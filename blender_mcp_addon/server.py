import socket
import json
import threading
import traceback
import queue
import bpy

from .tools.scene import SceneTools
from .tools.collections import CollectionTools
from .tools.modeling import ModelingTools
from .tools.materials import MaterialTools
from .tools.animation import AnimationTools
from .tools.rendering import RenderingTools
from .tools.camera import CameraTools
from .tools.lighting import LightTools
from .tools.history import HistoryTools


class BlenderMCPServer(
    SceneTools,
    CollectionTools,
    ModelingTools,
    MaterialTools,
    AnimationTools,
    RenderingTools,
    CameraTools,
    LightTools,
    HistoryTools,
):
    """Blender MCP Server for n8n with componentized tools"""

    def __init__(self):
        self.server_socket = None
        self.running = False
        self.server_thread = None
        self.command_queue = queue.Queue()
        self.last_error = None
        self.timer_handle = None

    def start_server(self, host="0.0.0.0", port=8888):
        if self.running:
            return
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind((host, port))
            self.server_socket.listen(128)  # Increased backlog for rapid n8n requests
            self.running = True
            self.server_thread = threading.Thread(target=self._server_loop, daemon=True)
            self.server_thread.start()
            self._register_timer()
            print(f"MCP Server started on {host}:{port}")
        except Exception as e:
            print(f"Failed to start server: {e}")
            traceback.print_exc()

    def _register_timer(self):
        if self.timer_handle:
            try:
                bpy.app.timers.unregister(self.timer_handle)
            except Exception:
                pass
        self.timer_handle = self._process_queue
        bpy.app.timers.register(self.timer_handle)

    def stop_server(self):
        self.running = False
        if self.server_socket:
            try:
                self.server_socket.close()
            except Exception:
                pass
        if self.timer_handle:
            try:
                bpy.app.timers.unregister(self.timer_handle)
            except Exception:
                pass
            self.timer_handle = None
        print("MCP Server stopped")

    def _server_loop(self):
        while self.running:
            try:
                self.server_socket.settimeout(1.0)
                try:
                    client, _ = self.server_socket.accept()
                    threading.Thread(
                        target=self._handle_client, args=(client,), daemon=True
                    ).start()
                except socket.timeout:
                    continue
            except Exception as e:
                if self.running:
                    print(f"[MCP] Server loop error: {e}")

    def _handle_client(self, client):
        try:
            client.settimeout(180.0)
            data = client.recv(8192)
            if not data:
                return
            command = json.loads(data.decode("utf-8"))
            response = self.handle_command(command)
            client.sendall(json.dumps(response).encode("utf-8"))
        except Exception as e:
            print(f"[MCP] Client error: {e}")
            try:
                client.sendall(
                    json.dumps({"status": "error", "message": str(e)}).encode("utf-8")
                )
            except Exception:
                pass
        finally:
            try:
                client.close()
            except Exception:
                pass

    def handle_command(self, command):
        if not self.running:
            return {"status": "error", "message": "Server not running"}
        result_event, res_container = threading.Event(), {"result": None}
        self.command_queue.put(
            {"command": command, "event": result_event, "container": res_container}
        )
        if not result_event.wait(timeout=60.0):
            return {"status": "error", "message": "Command timed out"}
        return res_container["result"]

    def _process_queue(self):
        if not self.running:
            return None
        try:
            while not self.command_queue.empty():
                try:
                    item = self.command_queue.get_nowait()
                    if not item:
                        continue
                    cmd, event, res = item["command"], item["event"], item["container"]
                    try:
                        res["result"] = self.execute_command(cmd)

                        # Push to Undo Stack if it's a state-changing command
                        cmd_type = cmd.get("type", "")
                        if (
                            cmd_type
                            and not cmd_type.startswith("get_")
                            and cmd_type
                            not in ["undo", "redo", "render_frame", "render_animation"]
                        ):
                            try:
                                bpy.ops.ed.undo_push(message=f"MCP: {cmd_type}")
                            except Exception as e:
                                print(f"[MCP] Warning: Failed to push undo step: {e}")

                    except Exception as e:
                        traceback.print_exc()
                        res["result"] = {
                            "status": "error",
                            "message": f"Execution error: {e}",
                        }
                    finally:
                        event.set()
                except Exception as e:
                    print(f"[MCP] Queue processing error: {e}")
                    traceback.print_exc()
        except Exception as e:
            print(f"[MCP] Critical Timer Error: {e}")
            traceback.print_exc()

        return 0.005

    def execute_command(self, command):
        cmd_type, params, rid = (
            command.get("type"),
            command.get("params", {}),
            command.get("request_id", "unknown"),
        )
        print(f"[MCP][{rid}] Executing: {cmd_type}")

        # Map types to methods (inherited from tool classes)
        # This keeps the dispatcher dynamic and maintains compatibility with existing client
        methods = {
            # Scene
            "get_scene_info": self.get_scene_info,
            "get_object_info": self.get_object_info,
            "get_viewport_screenshot": self.get_viewport_screenshot,
            "get_distance": self.get_distance,
            # Collections
            "create_collection": self.create_collection,
            "set_active_collection": self.set_active_collection,
            "move_to_collection": self.move_to_collection,
            "get_collections": self.get_collections,
            "remove_collection": self.remove_collection,
            # Modeling
            "create_primitive": self.create_primitive,
            "create_cube": self.create_cube,
            "create_cylinder": self.create_cylinder,
            "create_sphere": self.create_sphere,
            "create_icosphere": self.create_icosphere,
            "create_torus": self.create_torus,
            "create_text": self.create_text,
            "create_plane": self.create_plane,
            "duplicate_object": self.duplicate_object,
            "duplicate_selection": self.duplicate_selection,
            "create_and_array": self.create_and_array,
            "batch_transform": self.batch_transform,
            "apply_modifier": self.apply_modifier,
            "copy_modifier": self.copy_modifier,
            "remove_modifier": self.remove_modifier,
            "boolean_operation": self.boolean_operation,
            "transform_object": self.transform_object,
            "circular_array": self.circular_array,
            "select_objects": self.select_objects,
            "select_by_pattern": self.select_by_pattern,
            "delete_object": self.delete_object,
            "set_object_dimensions": self.set_object_dimensions,
            "join_objects": self.join_objects,
            "random_distribute": self.random_distribute,
            "extrude_mesh": self.extrude_mesh,
            "inset_faces": self.inset_faces,
            "shear_mesh": self.shear_mesh,
            "invert_mesh_selection": self.invert_mesh_selection,
            # Architectural (ArchBuilder)
            "build_room_shell": self.build_room_shell,
            "build_wall_segment": self.build_wall_segment,
            "build_wall_with_door": self.build_wall_with_door,
            "build_column": self.build_column,
            "toggle_ceiling": self.toggle_ceiling,
            "set_view": self.set_view,
            # Animation
            "set_keyframe": self.set_keyframe,
            "get_keyframes": self.get_keyframes,
            "set_timeline_range": self.set_timeline_range,
            "play_animation": self.play_animation,
            # Rendering
            "configure_render_settings": self.configure_render_settings,
            "render_frame": self.render_frame,
            "render_animation": self.render_animation,
            # Material
            "create_material": self.create_material,
            "set_material_properties": self.set_material_properties,
            "assign_material": self.assign_material,
            "add_shader_node": self.add_shader_node,
            "connect_shader_nodes": self.connect_shader_nodes,
            "assign_builtin_texture": self.assign_builtin_texture,
            "assign_texture_map": self.assign_texture_map,
            # Camera
            "create_camera": self.create_camera,
            "set_active_camera": self.set_active_camera,
            "camera_look_at": self.camera_look_at,
            # Light
            "create_light": self.create_light,
            "configure_light": self.configure_light,
            "set_world_background": self.set_world_background,
            # History
            "undo": self.undo_action,
            "redo": self.redo_action,
        }

        handler = methods.get(cmd_type)
        if not handler:
            return {"status": "error", "message": f"Unknown command: {cmd_type}"}

        try:
            result = handler(**params)
            if isinstance(result, dict) and "message" in result:
                msg = result["message"]
                if not msg.startswith(f"[{rid}]"):
                    result["message"] = (
                        f"✓ [{rid}] {msg[2:]}"
                        if msg.startswith("✓ ")
                        else f"[{rid}] {msg}"
                    )
            return {"status": "success", "result": result}
        except Exception as e:
            print(f"[MCP] Handler error: {e}")
            traceback.print_exc()
            return {"status": "error", "message": str(e)}

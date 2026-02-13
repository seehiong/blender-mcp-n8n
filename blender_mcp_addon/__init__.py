import bpy
from .server import BlenderMCPServer

bl_info = {
    "name": "Blender MCP for n8n",
    "author": "seehiong",
    "version": (0, 1, 2),
    "blender": (4, 0, 0),
    "location": "View3D > Sidebar > MCP",
    "description": "Blender Model Context Protocol (MCP) server for n8n",
    "category": "Development",
}

_server_instance = None


class BLENDERMCP_OT_StartServer(bpy.types.Operator):
    """Start MCP Server"""

    bl_idname = "blendermcp.start_server"
    bl_label = "Start MCP Server"

    def execute(self, context):
        global _server_instance
        if _server_instance is None:
            _server_instance = BlenderMCPServer()
        _server_instance.start_server()
        self.report({"INFO"}, "MCP Server started")
        return {"FINISHED"}


class BLENDERMCP_OT_StopServer(bpy.types.Operator):
    """Stop MCP Server"""

    bl_idname = "blendermcp.stop_server"
    bl_label = "Stop MCP Server"

    def execute(self, context):
        global _server_instance
        if _server_instance:
            _server_instance.stop_server()
            self.report({"INFO"}, "MCP Server stopped")
        return {"FINISHED"}


class BLENDERMCP_PT_Panel(bpy.types.Panel):
    """MCP Control Panel"""

    bl_label = "Blender MCP"
    bl_idname = "BLENDERMCP_PT_panel"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Blender MCP"

    def draw(self, context):
        global _server_instance
        layout = self.layout
        layout.label(text="Blender MCP for n8n")

        if _server_instance and _server_instance.running:
            row = layout.row()
            row.label(text="Status: Running", icon="CHECKMARK")
        else:
            row = layout.row()
            row.label(text="Status: Stopped", icon="X")
            row.alert = True

        layout.operator("blendermcp.start_server")
        layout.operator("blendermcp.stop_server")
        layout.separator()
        layout.label(text="Port: 9877")
        layout.label(text="45+ Structured Tools")


def register():
    bpy.utils.register_class(BLENDERMCP_OT_StartServer)
    bpy.utils.register_class(BLENDERMCP_OT_StopServer)
    bpy.utils.register_class(BLENDERMCP_PT_Panel)


def unregister():
    global _server_instance
    if _server_instance:
        _server_instance.stop_server()
        _server_instance = None
    bpy.utils.unregister_class(BLENDERMCP_PT_Panel)
    bpy.utils.unregister_class(BLENDERMCP_OT_StopServer)
    bpy.utils.unregister_class(BLENDERMCP_OT_StartServer)


if __name__ == "__main__":
    register()

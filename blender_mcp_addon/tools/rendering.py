import bpy


class RenderingTools:
    def configure_render_settings(
        self,
        engine=None,
        samples=None,
        resolution_x=None,
        resolution_y=None,
        output_path=None,
    ):
        """Configure render settings"""
        scene = bpy.context.scene

        if engine:
            scene.render.engine = engine
        if samples:
            if scene.render.engine == "CYCLES":
                scene.cycles.samples = samples
            elif scene.render.engine == "BLENDER_EEVEE":
                scene.eevee.taa_render_samples = samples
        if resolution_x:
            scene.render.resolution_x = resolution_x
        if resolution_y:
            scene.render.resolution_y = resolution_y
        if output_path:
            scene.render.filepath = output_path

        return {
            "success": True,
            "engine": scene.render.engine,
            "message": "Render settings updated",
        }

    def render_frame(self, output_path=None):
        """Render current frame"""
        if output_path:
            bpy.context.scene.render.filepath = output_path

        bpy.ops.render.render(write_still=True)

        return {
            "success": True,
            "output_path": bpy.context.scene.render.filepath,
            "message": "Frame rendered",
        }

    def render_animation(self, start_frame=None, end_frame=None, output_dir=None):
        """Render animation"""
        scene = bpy.context.scene

        if start_frame:
            scene.frame_start = start_frame
        if end_frame:
            scene.frame_end = end_frame
        if output_dir:
            scene.render.filepath = output_dir

        bpy.ops.render.render(animation=True)

        return {
            "success": True,
            "frames": f"{scene.frame_start}-{scene.frame_end}",
            "message": "Animation render started",
        }

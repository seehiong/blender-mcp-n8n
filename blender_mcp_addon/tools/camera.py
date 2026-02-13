import bpy
import math
from mathutils import Vector
from ..utils import get_object


class CameraTools:
    def create_camera(self, name, location, rotation, lens=50.0, type="PERSP"):
        """Create camera"""
        bpy.ops.object.camera_add(
            location=location, rotation=[math.radians(r) for r in rotation]
        )
        cam = bpy.context.active_object
        cam.name = name
        cam.data.lens = lens
        cam.data.type = type
        return {
            "success": True,
            "name": name,
            "message": f"Camera '{name}' created at {location}",
        }

    def set_active_camera(self, camera_name):
        """Set active camera"""
        cam = get_object(camera_name)
        bpy.context.scene.camera = cam
        return {"success": True, "message": f"✓ Camera '{camera_name}' set as active"}

    def camera_look_at(self, camera_name, target_location):
        """Point camera at target"""
        cam = get_object(camera_name)
        direction = Vector(target_location) - cam.location
        rot_quat = direction.to_track_quat("-Z", "Y")
        cam.rotation_euler = rot_quat.to_euler()
        return {
            "success": True,
            "message": f"Camera '{camera_name}' pointing at {target_location}",
        }

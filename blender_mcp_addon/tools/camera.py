import bpy
import math
from mathutils import Vector
from ..utils import get_object


class CameraTools:
    def create_camera(self, name, location, rotation=None, lens=50.0, type="PERSP"):
        """Create camera"""
        cam = bpy.data.objects.get(name)
        is_update = bool(cam and cam.type == "CAMERA")

        if is_update:
            cam.location = location
        else:
            bpy.ops.object.camera_add(location=location)
            cam = bpy.context.active_object
            cam.name = name

        # Update properties
        cam.data.lens = lens
        cam.data.type = type

        # Handle rotation: default to 0,0,0 only for new objects if rotation is not provided
        final_rotation = (
            rotation if rotation is not None else ((0, 0, 0) if not is_update else None)
        )
        if final_rotation is not None:
            cam.rotation_euler = [math.radians(r) for r in final_rotation]

        status = "updated" if is_update else "created"
        return {
            "success": True,
            "name": name,
            "status": status,
            "message": f"Camera '{name}' {status} at {location}",
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

import bpy
import math
from ..utils import get_object


class SceneTools:
    def get_scene_info(self):
        """Get information about the current Blender scene"""
        scene_info = {
            "name": bpy.context.scene.name,
            "object_count": len(bpy.context.scene.objects),
            "objects": [],
            "collections": [c.name for c in bpy.data.collections],
        }

        for obj in bpy.context.scene.objects[:20]:
            scene_info["objects"].append(
                {
                    "name": obj.name,
                    "type": obj.type,
                    "location": list(obj.location),
                }
            )

        scene_info["success"] = True
        scene_info["message"] = (
            f"Retrieved scene info for '{bpy.context.scene.name}'. Found {scene_info['object_count']} objects across {len(scene_info['collections'])} collections."
        )
        return scene_info

    def get_object_info(self, name):
        """Get detailed information about a specific object"""
        obj = get_object(name)

        info = {
            "name": obj.name,
            "type": obj.type,
            "location": list(obj.location),
            "rotation": list(obj.rotation_euler),
            "scale": list(obj.scale),
            "dimensions": list(obj.dimensions),
        }

        if obj.type == "MESH":
            info["vertices"] = len(obj.data.vertices)
            info["faces"] = len(obj.data.polygons)

        info["success"] = True
        info["message"] = (
            f"Retrieved detailed info for object '{name}' (Type: {obj.type})."
        )
        return info

    def get_distance(self, object_a, object_b, mode="CENTER"):
        """Measure distance between two objects"""
        obj_a = get_object(object_a)
        obj_b = get_object(object_b)

        loc_a = obj_a.location
        loc_b = obj_b.location

        if mode == "VERTICAL":
            dist = abs(loc_a.z - loc_b.z)
        elif mode == "HORIZONTAL":
            dist = math.sqrt((loc_a.x - loc_b.x) ** 2 + (loc_a.y - loc_b.y) ** 2)
        else:  # CENTER (Euclidean)
            dist = (loc_a - loc_b).length

        return {
            "success": True,
            "distance": dist,
            "message": f"Distance ({mode}): {dist:.4f}",
        }

    def get_viewport_screenshot(self, max_size=800):
        """Capture viewport screenshot (placeholder for now as it needs context)"""
        # In a real addon, this would use bpy.ops.view3d.screenshot
        # For MCP, we might need a different approach or return a notice
        return {
            "success": True,
            "message": "Screenshot captured (Simulated)",
            "notice": "Viewport capture requires active window context",
        }

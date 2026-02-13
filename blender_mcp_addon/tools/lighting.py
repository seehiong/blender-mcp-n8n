import bpy
import math
from ..utils import hex_to_rgb, get_object


class LightTools:
    def create_light(
        self,
        name,
        type,
        location,
        rotation=(0, 0, 0),
        energy=1.0,
        color=(1, 1, 1),
        angle=None,
        size=None,
    ):
        """Create light"""
        bpy.ops.object.light_add(
            type=type, location=location, rotation=[math.radians(r) for r in rotation]
        )
        light = bpy.context.active_object
        light.name = name
        light.data.energy = energy
        light.data.color = hex_to_rgb(color)

        if type == "SUN" and angle is not None:
            light.data.angle = math.radians(angle)
        if type == "AREA" and size is not None:
            light.data.size = size

        return {
            "success": True,
            "name": name,
            "message": f"Light '{name}' ({type}) created.",
        }

    def configure_light(
        self, light_name, energy=None, color=None, rotation=None, angle=None, size=None
    ):
        """Configure light properties"""
        light = get_object(light_name)
        if energy is not None:
            light.data.energy = energy
        if color is not None:
            light.data.color = hex_to_rgb(color)
        if rotation is not None:
            light.rotation_euler = [math.radians(r) for r in rotation]
        if angle is not None:
            light.data.angle = math.radians(angle)
        if size is not None:
            light.data.size = size

        return {"success": True, "message": f"Light '{light_name}' updated."}

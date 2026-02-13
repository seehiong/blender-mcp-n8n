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

    def set_world_background(
        self,
        mode="color",
        color=(0.05, 0.05, 0.05),
        strength=1.0,
        image_path=None,
        rotation_z=0.0,
    ):
        """
        Set the world background to a color, sky texture, or HDRI environment image.

        Args:
            mode: 'color', 'sky', or 'hdri'
            color: (r, g, b) tuple (used for 'color' mode)
            strength: Emission strength
            image_path: Absolute path to HDRI image (used for 'hdri' mode)
            rotation_z: Z-axis rotation in degrees (used for 'hdri')
        """
        world = bpy.context.scene.world
        if not world:
            world = bpy.data.worlds.new("World")
            bpy.context.scene.world = world

        world.use_nodes = True
        nodes = world.node_tree.nodes
        links = world.node_tree.links

        # Clear existing nodes
        nodes.clear()

        # Create Output
        output = nodes.new(type="ShaderNodeOutputWorld")
        output.location = (200, 0)

        # Create Background
        bg = nodes.new(type="ShaderNodeBackground")
        bg.location = (0, 0)
        bg.inputs["Strength"].default_value = strength
        links.new(bg.outputs["Background"], output.inputs["Surface"])

        if mode == "color":
            bg.inputs["Color"].default_value = (*hex_to_rgb(color), 1.0)
            return {
                "success": True,
                "message": f"World background set to solid color ({color})",
            }

        elif mode == "sky":
            sky = nodes.new(type="ShaderNodeTexSky")
            sky.location = (-300, 0)
            sky.sky_type = "NISHITA"
            links.new(sky.outputs["Color"], bg.inputs["Color"])
            return {
                "success": True,
                "message": "World background set to Nishita Sky Texture",
            }

        elif mode == "hdri":
            if not image_path:
                return {"success": False, "error": "image_path required for HDRI mode"}

            try:
                img = bpy.data.images.load(image_path)
            except Exception as e:
                return {"success": False, "error": f"Failed to load HDRI: {str(e)}"}

            env = nodes.new(type="ShaderNodeTexEnvironment")
            env.location = (-600, 0)
            env.image = img

            # Mapping setup for rotation
            mapping = nodes.new(type="ShaderNodeMapping")
            mapping.location = (-400, 0)
            mapping.inputs["Rotation"].default_value[2] = math.radians(rotation_z)

            coord = nodes.new(type="ShaderNodeTexCoord")
            coord.location = (-800, 0)

            links.new(coord.outputs["Generated"], mapping.inputs["Vector"])
            links.new(mapping.outputs["Vector"], env.inputs["Vector"])
            links.new(env.outputs["Color"], bg.inputs["Color"])

            return {
                "success": True,
                "message": f"World background set to HDRI: {image_path}",
            }

        return {"success": False, "error": f"Unknown mode: {mode}"}

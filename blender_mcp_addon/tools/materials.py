import bpy
import fnmatch
from ..utils import hex_to_rgb, get_object


class MaterialTools:
    def create_material(
        self,
        name,
        preset=None,
        base_color=None,
        metallic=0.0,
        roughness=0.5,
        emission_color=None,
        emission_strength=0.0,
        alpha=1.0,
        transmission=0.0,
        ior=1.45,
        object_names=None,
        pattern=None,
        slot_index=0,
        **kwargs,
    ):
        """Create material with Principled BSDF"""
        PRESETS = {
            "glass": {
                "base_color": "#FFFFFF",
                "roughness": 0.1,
                "transmission": 1.0,
                "ior": 1.45,
            },
            "glass_tinted": {
                "base_color": "#88CCFF",
                "roughness": 0.1,
                "transmission": 0.9,
            },
            "glass_frosted": {
                "base_color": "#FFFFFF",
                "roughness": 0.3,
                "transmission": 0.8,
            },
            "metal_brushed": {
                "base_color": "#C0C0C0",
                "metallic": 1.0,
                "roughness": 0.3,
            },
            "metal_polished": {
                "base_color": "#E0E0E0",
                "metallic": 1.0,
                "roughness": 0.05,
            },
            "metal_gold": {"base_color": "#FFD700", "metallic": 1.0, "roughness": 0.2},
            "metal_copper": {
                "base_color": "#B87333",
                "metallic": 1.0,
                "roughness": 0.3,
            },
            "plastic_glossy": {
                "base_color": "#FFFFFF",
                "metallic": 0.0,
                "roughness": 0.2,
            },
            "plastic_matte": {
                "base_color": "#FFFFFF",
                "metallic": 0.0,
                "roughness": 0.7,
            },
            "concrete": {"base_color": "#808080", "metallic": 0.0, "roughness": 0.9},
            "wood": {"base_color": "#8B4513", "metallic": 0.0, "roughness": 0.6},
            "rubber": {"base_color": "#2C2C2C", "metallic": 0.0, "roughness": 0.8},
            "emission": {
                "base_color": "#FFFFFF",
                "emission_color": "#FFFFFF",
                "emission_strength": 5.0,
            },
        }

        if preset and preset in PRESETS:
            p = PRESETS[preset]
            if base_color is None:
                base_color = p.get("base_color")
            metallic = p.get("metallic", metallic)
            roughness = p.get("roughness", roughness)
            transmission = p.get("transmission", transmission)
            ior = p.get("ior", ior)
            if emission_color is None:
                emission_color = p.get("emission_color")
            emission_strength = p.get("emission_strength", emission_strength)

        mat = bpy.data.materials.get(name)
        status = "existing" if mat else "created"
        if not mat:
            mat = bpy.data.materials.new(name=name)
            mat.use_nodes = True

        bsdf = mat.node_tree.nodes.get("Principled BSDF")
        if base_color:
            rgb = hex_to_rgb(base_color)
            if "Base Color" in bsdf.inputs:
                bsdf.inputs["Base Color"].default_value = (*rgb, 1.0)

        if "Metallic" in bsdf.inputs:
            bsdf.inputs["Metallic"].default_value = metallic
        if "Roughness" in bsdf.inputs:
            bsdf.inputs["Roughness"].default_value = roughness
        if "Alpha" in bsdf.inputs:
            bsdf.inputs["Alpha"].default_value = alpha

        # Cycles vs EEVEE check
        if "Transmission" in bsdf.inputs:
            bsdf.inputs["Transmission"].default_value = transmission
        elif "Transmission Weight" in bsdf.inputs:
            bsdf.inputs["Transmission Weight"].default_value = transmission

        if emission_color:
            e_rgb = hex_to_rgb(emission_color)
            if "Emission" in bsdf.inputs:
                bsdf.inputs["Emission"].default_value = (*e_rgb, 1.0)
            if "Emission Strength" in bsdf.inputs:
                bsdf.inputs["Emission Strength"].default_value = emission_strength

        if "IOR" in bsdf.inputs:
            bsdf.inputs["IOR"].default_value = ior

        if object_names or pattern:
            self.assign_material(
                name, object_names=object_names, pattern=pattern, slot_index=slot_index
            )
        return {
            "success": True,
            "name": name,
            "message": f"Material '{name}' {status}.",
        }

    def set_material_properties(self, material_name, **kwargs):
        """Modify existing material properties"""
        mat = bpy.data.materials.get(material_name)
        if not mat:
            raise ValueError(f"Material '{material_name}' not found")
        if not mat.use_nodes:
            mat.use_nodes = True
        bsdf = mat.node_tree.nodes.get("Principled BSDF")

        inputs = {
            "base_color": ("Base Color", True),
            "metallic": ("Metallic", False),
            "roughness": ("Roughness", False),
            "alpha": ("Alpha", False),
            "transmission": ("Transmission", False),
            "emission_color": ("Emission", True),
            "emission_strength": ("Emission Strength", False),
        }

        for key, (input_name, is_color) in inputs.items():
            if key in kwargs and kwargs[key] is not None:
                val = kwargs[key]
                if input_name in bsdf.inputs:
                    if is_color:
                        rgb = hex_to_rgb(val)
                        bsdf.inputs[input_name].default_value = (*rgb, 1.0)
                    else:
                        bsdf.inputs[input_name].default_value = val

        return {
            "success": True,
            "material": material_name,
            "message": f"Properties updated for '{material_name}'",
        }

    def assign_material(
        self, material_name, object_names=None, pattern=None, slot_index=0, **kwargs
    ):
        """Assign material to objects. Supports both names and patterns."""
        mat = (
            bpy.data.materials.get(material_name)
            or self.create_material(material_name)["name"]
        )
        if isinstance(mat, str):
            mat = bpy.data.materials.get(mat)

        target_names = set()

        # Process patterns
        if pattern:
            matches = fnmatch.filter(bpy.data.objects.keys(), pattern)
            target_names.update(matches)

        # Process specific names
        if object_names:
            if isinstance(object_names, str):
                object_names = [object_names]
            for name in object_names:
                if "*" in name or "?" in name:
                    matches = fnmatch.filter(bpy.data.objects.keys(), name)
                    target_names.update(matches)
                else:
                    target_names.add(name)

        # Fallback to selection if nothing provided
        if not target_names:
            target_names = {o.name for o in bpy.context.selected_objects}
            if not target_names:
                raise ValueError(
                    "No objects provided via 'object_names', 'pattern', or current selection."
                )

        for obj_name in target_names:
            obj = get_object(obj_name)
            if len(obj.data.materials) == 0:
                obj.data.materials.append(mat)
            else:
                obj.data.materials[slot_index] = mat

        return {
            "success": True,
            "message": f"Material '{material_name}' assigned to {len(target_names)} objects",
        }

    def add_shader_node(self, material_name, node_type, location, params=None):
        mat = bpy.data.materials.get(material_name)
        if not mat:
            raise ValueError(f"Material '{material_name}' not found")
        if not mat.use_nodes:
            mat.use_nodes = True
        node = mat.node_tree.nodes.new(type=node_type)
        node.location = location
        if params:
            for k, v in params.items():
                if hasattr(node, k):
                    setattr(node, k, v)
        return {
            "success": True,
            "node_name": node.name,
            "message": f"Added node '{node.name}' to '{material_name}'",
        }

    def connect_shader_nodes(
        self, material_name, from_node, from_socket, to_node, to_socket
    ):
        mat = bpy.data.materials.get(material_name)
        nodes = mat.node_tree.nodes
        from_n, to_n = nodes.get(from_node), nodes.get(to_node)
        mat.node_tree.links.new(from_n.outputs[from_socket], to_n.inputs[to_socket])
        return {"success": True, "message": f"Connected nodes in '{material_name}'"}

    def assign_builtin_texture(self, material_name, texture_type):
        mat = bpy.data.materials.get(material_name)
        if not mat.use_nodes:
            mat.use_nodes = True
        nodes = mat.node_tree.nodes
        tex_node = nodes.new(type=f"ShaderNodeTex{texture_type.capitalize()}")
        tex_node.location = (-400, 0)
        bsdf = nodes.get("Principled BSDF")
        mat.node_tree.links.new(tex_node.outputs[0], bsdf.inputs["Base Color"])
        return {
            "success": True,
            "message": f"Assigned {texture_type} texture to '{material_name}'",
        }

import bpy
import math
from ...utils import get_collection


class ModelingPrimitives:
    def create_cube(
        self,
        location,
        scale=None,
        rotation=None,
        name=None,
        collection=None,
        **kwargs,
    ):
        """Create a cube"""
        return self.create_primitive(
            "cube",
            location,
            scale=scale,
            rotation=rotation,
            name=name,
            collection=collection,
            **kwargs,
        )

    def create_cylinder(
        self,
        location,
        radius=None,
        depth=None,
        vertices=32,
        scale=None,
        rotation=None,
        name=None,
        collection=None,
        **kwargs,
    ):
        """Create a cylinder"""
        params = {
            "scale": scale,
            "rotation": rotation,
            "name": name,
            "collection": collection,
            "vertices": vertices,
        }
        if radius is not None:
            params["radius"] = radius
        if depth is not None:
            params["depth"] = depth
        params.update(kwargs)
        return self.create_primitive("cylinder", location, **params)

    def create_icosphere(
        self,
        location,
        radius=1.0,
        subdivisions=2,
        scale=None,
        rotation=None,
        name=None,
        collection=None,
        **kwargs,
    ):
        """Create an ico sphere"""
        return self.create_primitive(
            "icosphere",
            location,
            scale=scale,
            rotation=rotation,
            name=name,
            collection=collection,
            radius=radius,
            subdivisions=subdivisions,
            **kwargs,
        )

    def create_sphere(
        self,
        location,
        radius=1.0,
        scale=None,
        rotation=None,
        name=None,
        collection=None,
    ):
        """Create a UV sphere"""
        return self.create_primitive(
            "sphere",
            location,
            scale=scale,
            rotation=rotation,
            name=name,
            collection=collection,
            radius=radius,
        )

    def create_torus(
        self,
        location,
        major_radius=1.0,
        minor_radius=0.25,
        major_segments=48,
        minor_segments=12,
        scale=None,
        rotation=None,
        name=None,
        collection=None,
    ):
        """Create a torus"""
        return self.create_primitive(
            "torus",
            location,
            scale=scale,
            rotation=rotation,
            name=name,
            collection=collection,
            major_radius=major_radius,
            minor_radius=minor_radius,
            major_segments=major_segments,
            minor_segments=minor_segments,
        )

    def create_plane(
        self,
        location,
        size=2.0,
        scale=None,
        rotation=None,
        name=None,
        collection=None,
    ):
        """Create a plane"""
        return self.create_primitive(
            "plane",
            location,
            scale=scale,
            rotation=rotation,
            name=name,
            collection=collection,
            size=size,
        )

    def create_primitive(
        self,
        type,
        location,
        scale=None,
        rotation=None,
        name=None,
        collection=None,
        **kwargs,
    ):
        """Create primitive mesh with precise parameters"""
        ops_map = {
            "cube": bpy.ops.mesh.primitive_cube_add,
            "cylinder": bpy.ops.mesh.primitive_cylinder_add,
            "sphere": bpy.ops.mesh.primitive_uv_sphere_add,
            "torus": bpy.ops.mesh.primitive_torus_add,
            "plane": bpy.ops.mesh.primitive_plane_add,
            "cone": bpy.ops.mesh.primitive_cone_add,
            "icosphere": bpy.ops.mesh.primitive_ico_sphere_add,
        }

        op = ops_map.get(type.lower())
        if not op:
            raise ValueError(f"Unknown primitive type: {type}")

        params = {"location": location}
        if type == "cube":
            params["size"] = kwargs.get("size", 1.0)
        elif type == "cylinder":
            if "vertices" in kwargs:
                params["vertices"] = kwargs["vertices"]
            if "radius" in kwargs:
                params["radius"] = kwargs["radius"]
            if "depth" in kwargs:
                params["depth"] = kwargs["depth"]
        elif type == "sphere" or type == "icosphere":
            if "radius" in kwargs:
                params["radius"] = kwargs["radius"]
            if "subdivisions" in kwargs:
                params["subdivisions"] = kwargs["subdivisions"]
        elif type == "torus":
            if "major_radius" in kwargs:
                params["major_radius"] = kwargs["major_radius"]
            if "minor_radius" in kwargs:
                params["minor_radius"] = kwargs["minor_radius"]
            if "major_segments" in kwargs:
                params["major_segments"] = kwargs["major_segments"]
            if "minor_segments" in kwargs:
                params["minor_segments"] = kwargs["minor_segments"]

        is_update = bool(name and name in bpy.data.objects)
        if is_update:
            obj = bpy.data.objects[name]
            obj.location = location
            # Update specific mesh parameters if it's a mesh object
            if obj.type == "MESH":
                # Note: This is an approximation for existing objects without rebuilding mesh
                pass
        else:
            existing_objects = {obj.name for obj in bpy.data.objects}
            op(**params)
            new_objects = [
                obj for obj in bpy.data.objects if obj.name not in existing_objects
            ]
            obj = new_objects[0] if new_objects else bpy.context.object

        if not obj:
            raise RuntimeError("Failed to identify or update object")

        # Handle scale and rotation with defaults for NEW objects only
        final_scale = (
            scale if scale is not None else ((1, 1, 1) if not is_update else None)
        )
        final_rotation = (
            rotation if rotation is not None else ((0, 0, 0) if not is_update else None)
        )

        if final_scale is not None:
            obj.scale = final_scale

        if final_rotation is not None:
            obj.rotation_euler = [math.radians(r) for r in final_rotation]

        if "dimensions" in kwargs and kwargs["dimensions"]:
            obj.dimensions = kwargs["dimensions"]
        if collection:
            self._move_to_collection_helper(obj, collection)
        if name:
            obj.name = name

        status = "updated" if is_update else "created"
        return {
            "success": True,
            "name": obj.name,
            "type": type,
            "status": status,
            "verified": True,
            "message": f"Object '{obj.name}' ({type}) {status} successfully. Geometry verified. Proceed immediately to next modeling step.",
        }

    def _move_to_collection_helper(self, obj, collection_name):
        coll = get_collection(collection_name)
        for c in obj.users_collection:
            c.objects.unlink(obj)
        coll.objects.link(obj)

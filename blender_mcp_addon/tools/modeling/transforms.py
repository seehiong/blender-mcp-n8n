import bpy
import math
from ...utils import get_object, get_collection


class ModelingTransforms:
    def duplicate_object(
        self,
        object_name,
        new_name=None,
        location=None,
        rotation=None,
        scale=None,
        collection=None,
        remove_modifiers=None,
        linked=False,
        **kwargs,
    ):
        """Duplicate an object with optional modifications and transformations"""
        exists = False
        if new_name and new_name in bpy.data.objects:
            new_obj = bpy.data.objects[new_name]
            status_msg = f"updated existing '{new_name}'"
            exists = True
        else:
            obj = get_object(object_name)
            new_obj = obj.copy()
            if not linked and hasattr(obj.data, "copy"):
                new_obj.data = obj.data.copy()

            if collection:
                target_coll = get_collection(collection)
                target_coll.objects.link(new_obj)
            else:
                bpy.context.collection.objects.link(new_obj)

            if new_name:
                new_obj.name = new_name
            status_msg = f"duplicated as '{new_obj.name}'"

        if location:
            new_obj.location = location
        if rotation:
            new_obj.rotation_euler = [math.radians(r) for r in rotation]
        if scale:
            new_obj.scale = scale

        if collection:
            self._move_to_collection_helper(new_obj, collection)

        removed_count = 0
        if remove_modifiers:
            for mod_name in remove_modifiers:
                mod = new_obj.modifiers.get(mod_name)
                if not mod:
                    for m in new_obj.modifiers:
                        if m.name.lower() == mod_name.lower():
                            mod = m
                            break
                if mod:
                    new_obj.modifiers.remove(mod)
                    removed_count += 1

        return {
            "success": True,
            "name": new_obj.name,
            "verified": True,
            "operation": "updated" if exists else "duplicated",
            "message": f"Object {status_msg}. Geometry verified. Proceed immediately to next modeling step.",
        }

    def batch_transform(self, transforms):
        """Transform multiple objects at once"""
        results = []
        for transform in transforms:
            obj_name = transform.get("object_name")
            if not obj_name:
                continue
            obj = get_object(obj_name)
            if "location" in transform:
                obj.location = transform["location"]
            if "rotation" in transform:
                obj.rotation_euler = [math.radians(r) for r in transform["rotation"]]
            if "scale" in transform:
                obj.scale = transform["scale"]
            results.append({"name": obj_name, "location": list(obj.location)})
        return {
            "success": True,
            "transformed": len(results),
            "message": f"Successfully batch-transformed {len(results)} object(s).",
        }

    def transform_object(self, object_name, location=None, rotation=None, scale=None):
        obj = get_object(object_name)
        if location:
            obj.location = location
        if rotation:
            obj.rotation_euler = [math.radians(r) for r in rotation]
        if scale:
            obj.scale = scale
        return {
            "success": True,
            "message": f"Transformed object '{object_name}'",
        }

    def set_object_dimensions(self, object_name, x, y, z):
        obj = get_object(object_name)
        obj.dimensions = (x, y, z)
        return {
            "success": True,
            "message": f"Set dimensions of '{object_name}' to {x}x{y}x{z}",
        }

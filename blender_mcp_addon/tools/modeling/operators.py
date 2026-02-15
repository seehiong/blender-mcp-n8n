import bpy
import math
import random
from ...utils import get_object, get_collection


class ModelingOperators:
    def create_and_array(
        self,
        primitive_type,
        location,
        name=None,
        array_count=2,
        array_offset=(0, 0, 1),
        scale=(1, 1, 1),
        rotation=(0, 0, 0),
        **primitive_kwargs,
    ):
        """Create primitive + apply ARRAY modifier"""
        # Note: self refers to the combined ModelingTools class
        result = self.create_primitive(
            primitive_type,
            location,
            scale=scale,
            rotation=rotation,
            name=name,
            **primitive_kwargs,
        )
        obj_name = result["name"]
        mod_result = self.apply_modifier(
            obj_name,
            "ARRAY",
            count=array_count,
            use_relative_offset=False,
            use_constant_offset=True,
            constant_offset_displace=array_offset,
        )
        return {
            "success": True,
            "name": obj_name,
            "type": primitive_type,
            "modifier": mod_result["modifier_name"],
            "message": f"Created '{obj_name}' with array modifier.",
        }

    def circular_array(
        self,
        object_name,
        count,
        radius,
        center=(0, 0, 0),
        start_angle=0,
        axis="Z",
        use_radial_rotation=True,
        collection=None,
        join_immediately=False,
        joined_name=None,
        **kwargs,
    ):
        obj = get_object(object_name)
        created = []
        angle_step = 360.0 / count
        for i in range(count):
            angle_rad = math.radians(start_angle + i * angle_step)
            if axis == "Z":
                x, y, z = (
                    center[0] + radius * math.cos(angle_rad),
                    center[1] + radius * math.sin(angle_rad),
                    center[2],
                )
                rot = (0, 0, angle_rad) if use_radial_rotation else (0, 0, 0)
            elif axis == "Y":
                x, y, z = (
                    center[0] + radius * math.cos(angle_rad),
                    center[1],
                    center[2] + radius * math.sin(angle_rad),
                )
                rot = (0, angle_rad, 0) if use_radial_rotation else (0, 0, 0)
            else:
                x, y, z = (
                    center[0],
                    center[1] + radius * math.cos(angle_rad),
                    center[2] + radius * math.sin(angle_rad),
                )
                rot = (angle_rad, 0, 0) if use_radial_rotation else (0, 0, 0)

            if i == 0:
                obj.location = (x, y, z)
                if use_radial_rotation:
                    obj.rotation_euler = rot
                if collection:
                    self._move_to_collection_helper(obj, collection)
                created.append(obj.name)
            else:
                new_obj = obj.copy()
                new_obj.data = obj.data.copy()
                if collection:
                    coll = get_collection(collection)
                else:
                    coll = (
                        obj.users_collection[0]
                        if obj.users_collection
                        else bpy.context.collection
                    )
                coll.objects.link(new_obj)
                new_obj.location = (x, y, z)
                if use_radial_rotation:
                    new_obj.rotation_euler = rot
                created.append(new_obj.name)

        # AUTO-SELECT ALL CREATED OBJECTS
        bpy.ops.object.select_all(action="DESELECT")
        for name in created:
            o = bpy.data.objects.get(name)
            if o:
                o.select_set(True)
        if created:
            bpy.context.view_layer.objects.active = bpy.data.objects.get(created[0])

        if join_immediately:
            join_res = self.join_objects(
                object_names=created, new_name=joined_name or f"{object_name}_Joined"
            )
            return {
                "success": True,
                "name": join_res["name"],
                "message": f"Created circular array of {count} objects and joined them into '{join_res['name']}'.",
            }

        summary = ", ".join(created[:3])
        if len(created) > 3:
            summary += f", and {len(created) - 3} others"

        return {
            "success": True,
            "names": created,
            "verified": True,
            "message": f"Created circular array of {count} objects and selected them: ({summary}). All geometry verified. Proceed immediately to next modeling step.",
        }

    def join_objects(
        self,
        object_names=None,
        active_object=None,
        new_name=None,
        pattern=None,
        **kwargs,
    ):
        """Join objects. If pattern is provided, it selects matching objects first."""
        if pattern:
            self.select_by_pattern(pattern)
            object_names = [o.name for o in bpy.context.selected_objects]

        if object_names:
            if not active_object and len(object_names) > 0:
                active_object = object_names[0]
            self.select_objects(object_names, active_object)

        if not bpy.context.selected_objects:
            raise ValueError("No objects selected to join")

        if not bpy.context.view_layer.objects.active and bpy.context.selected_objects:
            bpy.context.view_layer.objects.active = bpy.context.selected_objects[0]

        bpy.ops.object.join()
        res = bpy.context.active_object
        if new_name:
            res.name = new_name
        return {
            "success": True,
            "message": f"Joined objects into '{res.name}'",
        }

    def random_distribute(
        self, object_name, count, min_distance, max_distance, z_position=0.0, seed=None
    ):
        if seed is not None:
            random.seed(seed)
        obj = get_object(object_name)
        created = []
        for _ in range(count):
            while True:
                x, y = (
                    random.uniform(-max_distance, max_distance),
                    random.uniform(-max_distance, max_distance),
                )
                if min_distance <= math.sqrt(x**2 + y**2) <= max_distance:
                    break
            new_obj = obj.copy()
            new_obj.data = obj.data.copy()
            bpy.context.collection.objects.link(new_obj)
            new_obj.location = (x, y, z_position)
            created.append(new_obj.name)
        return {
            "success": True,
            "message": f"Distributed {len(created)} copies.",
        }
        return {
            "success": True,
            "message": f"Distributed {len(created)} copies.",
        }

    def extrude_mesh(self, object_name, mode="FACES", move=(0, 0, 0)):
        obj = get_object(object_name)
        bpy.context.view_layer.objects.active = obj
        bpy.ops.object.mode_set(mode="EDIT")
        bpy.ops.mesh.select_all(action="SELECT")

        select_mode = (mode == "VERTS", mode == "EDGES", mode == "FACES")
        bpy.context.tool_settings.mesh_select_mode = select_mode

        bpy.ops.mesh.extrude_region_move(TRANSFORM_OT_translate={"value": move})
        bpy.ops.object.mode_set(mode="OBJECT")
        return {
            "success": True,
            "message": f"Extruded {mode.lower()} of '{object_name}' by {move}.",
        }

    def inset_faces(self, object_name, thickness, depth=0.0):
        obj = get_object(object_name)
        bpy.context.view_layer.objects.active = obj
        bpy.ops.object.mode_set(mode="EDIT")
        bpy.ops.mesh.select_all(action="SELECT")

        bpy.ops.mesh.inset(thickness=thickness, depth=depth)

        bpy.ops.object.mode_set(mode="OBJECT")
        return {
            "success": True,
            "message": f"Inset faces of '{object_name}' by {thickness}.",
        }

    def shear_mesh(self, object_name, value, axis="X", orient_axis="Z"):
        obj = get_object(object_name)
        bpy.context.view_layer.objects.active = obj
        bpy.ops.object.mode_set(mode="EDIT")
        bpy.ops.mesh.select_all(action="SELECT")

        bpy.ops.transform.shear(
            value=value, orient_axis=orient_axis, orient_axis_ortho=axis
        )

        bpy.ops.object.mode_set(mode="OBJECT")
        return {
            "success": True,
            "message": f"Sheared '{object_name}' on {axis} axis.",
        }

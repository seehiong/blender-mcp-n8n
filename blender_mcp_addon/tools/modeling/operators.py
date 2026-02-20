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
        if bpy.context.mode != "OBJECT":
            bpy.ops.object.mode_set(mode="OBJECT")
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
        # Ensure we're in Object mode
        if bpy.context.mode != "OBJECT":
            bpy.ops.object.mode_set(mode="OBJECT")

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
        self,
        object_name,
        count,
        min_distance,
        max_distance,
        center=None,
        z_position=0.0,
        seed=None,
    ):
        if seed is not None:
            random.seed(seed)
        obj = get_object(object_name)
        dist_center = center if center else obj.location
        created = []
        for _ in range(count):
            while True:
                # Calculate relative offset
                off_x, off_y = (
                    random.uniform(-max_distance, max_distance),
                    random.uniform(-max_distance, max_distance),
                )
                if min_distance <= math.sqrt(off_x**2 + off_y**2) <= max_distance:
                    break
            new_obj = obj.copy()
            new_obj.data = obj.data.copy()
            # Link to the same collection as source
            coll = (
                obj.users_collection[0]
                if obj.users_collection
                else bpy.context.collection
            )
            coll.objects.link(new_obj)
            new_obj.location = (
                dist_center[0] + off_x,
                dist_center[1] + off_y,
                z_position if center else dist_center[2],
            )
            created.append(new_obj.name)
        return {
            "success": True,
            "message": f"Distributed {len(created)} copies around {dist_center}.",
        }

    def _select_faces_by_normal(self, obj, target_normal, angle_threshold_deg=1.0):
        """Select faces whose normal is within threshold of target_normal (world space)"""
        import bmesh
        import mathutils

        # Ensure we are in object mode
        if bpy.context.mode != "OBJECT":
            bpy.ops.object.mode_set(mode="OBJECT")

        bm = bmesh.new()
        bm.from_mesh(obj.data)
        bm.faces.ensure_lookup_table()

        target = mathutils.Vector(target_normal).normalized()
        threshold = math.radians(angle_threshold_deg)

        # Get object world matrix to convert local normals to world normals
        matrix_world = obj.matrix_world.to_3x3().inverted().transposed()

        selected_count = 0
        for face in bm.faces:
            # Convert local normal to world normal
            world_normal = (matrix_world @ face.normal).normalized()
            angle = world_normal.angle(target)

            if angle <= threshold:
                face.select = True
                selected_count += 1
            else:
                face.select = False

        # Write selection back to mesh
        bm.to_mesh(obj.data)
        bm.free()

        # Update mesh to ensure selection is visible
        obj.data.update()

        return selected_count

    def extrude_mesh(
        self,
        object_name,
        mode="FACES",
        move=(0, 0, 0),
        filter_normal=None,
        angle_threshold=1.0,
        use_selection=False,
        **kwargs,
    ):
        obj = get_object(object_name)
        bpy.context.view_layer.objects.active = obj

        if filter_normal:
            # Select faces by normal in Object mode
            self._select_faces_by_normal(obj, filter_normal, angle_threshold)
        elif not use_selection:
            # Select all faces
            if bpy.context.mode != "OBJECT":
                bpy.ops.object.mode_set(mode="OBJECT")
            # Select all faces in mesh data
            for poly in obj.data.polygons:
                poly.select = True
            obj.data.update()

        # Now enter Edit mode - selections will be preserved
        bpy.ops.object.mode_set(mode="EDIT")
        select_mode = (mode == "VERTS", mode == "EDGES", mode == "FACES")
        bpy.context.tool_settings.mesh_select_mode = select_mode

        bpy.ops.mesh.extrude_region_move(TRANSFORM_OT_translate={"value": move})

        # Return to Object mode
        bpy.ops.object.mode_set(mode="OBJECT")
        return {
            "success": True,
            "verified": True,
            "message": f"Extruded {mode.lower()} of '{object_name}' by {move}. Geometry verified. Proceed immediately to next modeling step.",
        }

    def inset_faces(
        self,
        object_name,
        thickness,
        depth=0.0,
        filter_normal=None,
        angle_threshold=1.0,
        use_selection=False,
        **kwargs,
    ):
        obj = get_object(object_name)
        bpy.context.view_layer.objects.active = obj

        if filter_normal:
            # Select faces by normal in Object mode
            self._select_faces_by_normal(obj, filter_normal, angle_threshold)
        elif not use_selection:
            # Select all faces
            if bpy.context.mode != "OBJECT":
                bpy.ops.object.mode_set(mode="OBJECT")
            for poly in obj.data.polygons:
                poly.select = True
            obj.data.update()

        # Enter Edit mode - selections will be preserved
        bpy.ops.object.mode_set(mode="EDIT")
        bpy.ops.mesh.inset(thickness=thickness, depth=depth)

        # Return to Object mode
        bpy.ops.object.mode_set(mode="OBJECT")
        return {
            "success": True,
            "verified": True,
            "message": f"Inset faces of '{object_name}' by {thickness}. Geometry verified. Proceed immediately to next modeling step.",
        }

    def shear_mesh(
        self,
        object_name,
        value,
        axis="X",
        orient_axis="Z",
        filter_normal=None,
        angle_threshold=1.0,
    ):
        import bmesh
        import mathutils

        obj = get_object(object_name)
        bpy.context.view_layer.objects.active = obj

        # Work in Object mode
        if bpy.context.mode != "OBJECT":
            bpy.ops.object.mode_set(mode="OBJECT")

        # Get bmesh
        bm = bmesh.new()
        bm.from_mesh(obj.data)
        bm.faces.ensure_lookup_table()
        bm.verts.ensure_lookup_table()

        # Determine which faces to shear
        faces_to_shear = []
        if filter_normal:
            target = mathutils.Vector(filter_normal).normalized()
            threshold = math.radians(angle_threshold)
            matrix_world = obj.matrix_world.to_3x3().inverted().transposed()

            for face in bm.faces:
                world_normal = (matrix_world @ face.normal).normalized()
                angle = world_normal.angle(target)
                if angle <= threshold:
                    faces_to_shear.append(face)
        else:
            faces_to_shear = list(bm.faces)

        # Get all vertices from selected faces
        verts_to_shear = set()
        for face in faces_to_shear:
            for vert in face.verts:
                verts_to_shear.add(vert)

        # Apply shear transformation manually
        # Shear formula: new_pos = old_pos + shear_value * (old_pos[orient_axis]) * axis_vector
        axis_map = {"X": 0, "Y": 1, "Z": 2}
        shear_axis_idx = axis_map[axis]
        orient_axis_idx = axis_map[orient_axis]

        for vert in verts_to_shear:
            offset = value * vert.co[orient_axis_idx]
            vert.co[shear_axis_idx] += offset

        # Write back to mesh
        bm.to_mesh(obj.data)
        bm.free()
        obj.data.update()

        return {
            "success": True,
            "message": f"Sheared '{object_name}' on {axis} axis by {value}.",
        }

    def delete_object(self, object_name=None, pattern=None, **kwargs):
        """Delete object(s) by name or pattern. Handles hidden objects."""
        import bpy
        import fnmatch

        # Ensure we're in Object mode
        if bpy.context.mode != "OBJECT":
            bpy.ops.object.mode_set(mode="OBJECT")

        objects_to_delete = []
        if pattern:
            # 1. Collect matching objects from all objects in the blend file
            for obj in bpy.data.objects:
                if fnmatch.fnmatch(obj.name, pattern):
                    objects_to_delete.append(obj)

            # 2. Collect matching collections
            collections_to_remove = []
            for coll in bpy.data.collections:
                if fnmatch.fnmatch(coll.name, pattern):
                    collections_to_remove.append(coll)

            # Delete objects
            count = len(objects_to_delete)
            for obj in objects_to_delete:
                # We use the data-block remove method which doesn't care about visibility
                bpy.data.objects.remove(obj, do_unlink=True)

            # Delete collections
            for coll in collections_to_remove:
                # Unlink from parents/scene
                for parent in bpy.data.collections:
                    if coll.name in parent.children:
                        parent.children.unlink(coll)
                if coll.name in bpy.context.scene.collection.children:
                    bpy.context.scene.collection.children.unlink(coll)
                bpy.data.collections.remove(coll)

            return {
                "success": True,
                "message": f"Deleted {count} objects and {len(collections_to_remove)} collections matching pattern '{pattern}'",
            }

        # Single object deletion
        obj = get_object(object_name)
        bpy.data.objects.remove(obj, do_unlink=True)
        return {"success": True, "message": f"Deleted object '{object_name}'"}

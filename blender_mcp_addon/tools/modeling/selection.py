import bpy
import fnmatch
from ...utils import get_object


class ModelingSelection:
    def select_objects(self, object_names, active_object=None):
        if isinstance(object_names, str):
            object_names = [object_names]

        bpy.ops.object.select_all(action="DESELECT")

        expanded_names = []
        for name in object_names:
            if "*" in name or "?" in name:
                matches = fnmatch.filter(bpy.data.objects.keys(), name)
                expanded_names.extend(matches)
            else:
                expanded_names.append(name)

        for name in expanded_names:
            get_object(name).select_set(True)
        if active_object:
            bpy.context.view_layer.objects.active = get_object(active_object)
        return {
            "success": True,
            "message": f"Selected {len(expanded_names)} objects. TIP: If your goal is material assignment, use 'create_material(..., pattern=\"*\")' instead to avoid rate limits.",
        }

    def select_by_pattern(self, pattern, extend=False, **kwargs):
        """Select objects matching a glob pattern (e.g. 'Facade_Fin*')"""
        # Ensure we're in Object mode
        if bpy.context.mode != "OBJECT":
            bpy.ops.object.mode_set(mode="OBJECT")

        if not extend:
            bpy.ops.object.select_all(action="DESELECT")

        bpy.ops.object.select_pattern(pattern=pattern, extend=extend)

        initial_selected = list(bpy.context.selected_objects)
        greedy_note = ""

        if len(initial_selected) == 1 and not any(c in pattern for c in "*?"):
            base_name = initial_selected[0].name
            sibling_pattern = f"{base_name}.*"
            bpy.ops.object.select_pattern(pattern=sibling_pattern, extend=True)

            final_selected = bpy.context.selected_objects
            if len(final_selected) > 1:
                greedy_note = (
                    f" (Included {len(final_selected) - 1} siblings automatically)"
                )

        selected = [o.name for o in bpy.context.selected_objects]
        active = bpy.context.view_layer.objects.active

        summary = ", ".join(selected[:3])
        if len(selected) > 3:
            summary += f", and {len(selected) - 3} others"

        return {
            "success": True,
            "count": len(selected),
            "names": selected,
            "active_object": active.name if active else None,
            "message": f"Selected {len(selected)} object(s) matching '{pattern}': ({summary}){greedy_note}. TIP: For materials, use the 'pattern' parameter inside the material tool directly.",
        }

import bpy
from ...utils import get_object


class ModelingModifiers:
    def apply_modifier(
        self, object_name, modifier_type, name=None, target_objects=None, **kwargs
    ):
        """Add and configure modifier"""
        obj = get_object(object_name)
        mod_name = name or modifier_type
        mod = obj.modifiers.get(mod_name)
        if not mod:
            for m in obj.modifiers:
                if m.name.lower() == mod_name.lower() and m.type == modifier_type:
                    mod = m
                    break
        if not mod:
            mod = obj.modifiers.new(name=mod_name, type=modifier_type)

        if modifier_type == "ARRAY":
            if "count" in kwargs:
                mod.count = kwargs["count"]
            if "use_relative_offset" in kwargs:
                mod.use_relative_offset = kwargs["use_relative_offset"]
            if "use_constant_offset" in kwargs:
                mod.use_constant_offset = kwargs["use_constant_offset"]
            if "constant_offset_displace" in kwargs:
                mod.constant_offset_displace = kwargs["constant_offset_displace"]
        elif modifier_type == "MIRROR":
            if "use_axis" in kwargs:
                mod.use_axis = kwargs["use_axis"]
        elif modifier_type == "SUBSURF":
            if "levels" in kwargs:
                mod.levels = kwargs["levels"]

        if not target_objects:
            selected = [
                o.name
                for o in bpy.context.selected_objects
                if o.name != object_name and o.name != obj.name
            ]
            if selected:
                target_objects = selected

        if target_objects:
            self.copy_modifier(object_name, target_objects, mod.name)
        return {
            "success": True,
            "modifier_name": mod.name,
            "message": f"Applied modifier '{mod.name}' to '{object_name}'.",
        }

    def copy_modifier(self, source_object, target_objects, modifier_name):
        """Copy modifier from source to target objects"""
        source = get_object(source_object)
        source_mod = source.modifiers.get(modifier_name)
        if not source_mod:
            raise ValueError(
                f"Modifier '{modifier_name}' not found on '{source_object}'"
            )

        count = 0
        for target_name in target_objects:
            if target_name == source_object:
                continue
            target = get_object(target_name)
            new_mod = target.modifiers.get(source_mod.name)
            if not new_mod:
                for m in target.modifiers:
                    if (
                        m.name.lower() == source_mod.name.lower()
                        and m.type == source_mod.type
                    ):
                        new_mod = m
                        break
            if not new_mod:
                new_mod = target.modifiers.new(
                    name=source_mod.name, type=source_mod.type
                )

            exclude = {
                "bl_rna",
                "rna_type",
                "type",
                "name",
                "is_active",
                "is_override_library",
            }
            for prop in dir(source_mod):
                if prop.startswith("_") or prop in exclude:
                    continue
                try:
                    val = getattr(source_mod, prop)
                    if not callable(val):
                        setattr(new_mod, prop, val)
                except Exception:
                    pass
            count += 1
        return {
            "success": True,
            "message": f"Copied modifier '{modifier_name}' to {count} object(s)",
        }

    def remove_modifier(self, object_name, modifier_name):
        obj = get_object(object_name)
        mod = obj.modifiers.get(modifier_name)
        if not mod:
            raise ValueError(f"Modifier '{modifier_name}' not found")
        obj.modifiers.remove(mod)
        return {
            "success": True,
            "message": f"Modifier '{modifier_name}' removed from '{object_name}'",
        }

    def boolean_operation(self, object_a, object_b, operation):
        obj_a = get_object(object_a)
        obj_b = get_object(object_b)
        mod = obj_a.modifiers.new(name="Boolean", type="BOOLEAN")
        mod.operation = operation
        mod.object = obj_b
        return {
            "success": True,
            "message": f"Applied Boolean ({operation}) on '{object_a}'",
        }

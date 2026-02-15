import bpy


def hex_to_rgb(hex_color):
    """Convert hex color string to RGB tuple"""
    if isinstance(hex_color, str) and hex_color.startswith("#"):
        hex_color = hex_color.lstrip("#")
        return tuple(int(hex_color[i : i + 2], 16) / 255.0 for i in (0, 2, 4))
    return hex_color


def get_object(name):
    """Get object by name with error handling"""
    obj = bpy.data.objects.get(name)
    if not obj:
        raise ValueError(f"Object '{name}' not found")
    return obj


def get_collection(name):
    """Get collection by name, creating it if it doesn't exist"""
    coll = bpy.data.collections.get(name)
    if not coll:
        coll = bpy.data.collections.new(name)
        bpy.context.scene.collection.children.link(coll)
    return coll

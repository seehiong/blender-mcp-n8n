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
    """Get collection by name with error handling"""
    coll = bpy.data.collections.get(name)
    if not coll:
        raise ValueError(f"Collection '{name}' not found")
    return coll

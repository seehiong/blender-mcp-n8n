import bpy
from ..utils import get_collection, get_object


class CollectionTools:
    def create_collection(self, name, parent_collection=None, **kwargs):
        """Create new collection"""
        new_collection = bpy.data.collections.new(name)

        if parent_collection:
            parent = get_collection(parent_collection)
            parent.children.link(new_collection)
        else:
            bpy.context.scene.collection.children.link(new_collection)

        return {
            "success": True,
            "name": name,
            "message": f"Collection '{name}' created successfully.",
        }

    def set_active_collection(self, collection_name):
        """Set active collection for new objects"""
        get_collection(collection_name)

        layer_collection = bpy.context.view_layer.layer_collection
        for lc in self._find_layer_collection(layer_collection, collection_name):
            bpy.context.view_layer.active_layer_collection = lc
            return {
                "success": True,
                "active_collection": collection_name,
                "message": f"Collection '{collection_name}' is now set as the active collection for new objects.",
            }

        raise ValueError(f"Could not set active collection '{collection_name}'")

    def _find_layer_collection(self, layer_collection, name):
        """Recursively find layer collection by name"""
        if layer_collection.collection.name == name:
            yield layer_collection
        for child in layer_collection.children:
            yield from self._find_layer_collection(child, name)

    def move_to_collection(self, object_names, collection_name, **kwargs):
        """Move objects to collection"""
        collection = get_collection(collection_name)

        for obj_name in object_names:
            obj = get_object(obj_name)

            for coll in obj.users_collection:
                coll.objects.unlink(obj)

            collection.objects.link(obj)

        return {
            "success": True,
            "moved": len(object_names),
            "message": f"Successfully moved {len(object_names)} object(s) to collection '{collection_name}'",
        }

    def get_collections(self):
        """List all collections"""

        def build_hierarchy(collection, level=0):
            return {
                "name": collection.name,
                "level": level,
                "objects": [obj.name for obj in collection.objects],
                "children": [
                    build_hierarchy(child, level + 1) for child in collection.children
                ],
            }

        return build_hierarchy(bpy.context.scene.collection)

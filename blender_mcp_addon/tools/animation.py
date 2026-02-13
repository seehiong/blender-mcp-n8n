import bpy
import math
from ..utils import get_object


class AnimationTools:
    def set_keyframe(self, object_name, property_path, frame, value):
        """Set keyframe for object property"""
        obj = get_object(object_name)

        if property_path == "location":
            obj.location = value
            obj.keyframe_insert(data_path="location", frame=frame)
        elif property_path == "rotation":
            obj.rotation_euler = [math.radians(v) for v in value]
            obj.keyframe_insert(data_path="rotation_euler", frame=frame)
        elif property_path == "scale":
            obj.scale = value
            obj.keyframe_insert(data_path="scale", frame=frame)
        else:
            raise ValueError(f"Unsupported property: {property_path}")

        return {
            "success": True,
            "frame": frame,
            "message": f"Set keyframe for '{property_path}' at frame {frame}",
        }

    def get_keyframes(self, object_name):
        """Get all keyframes for an object"""
        obj = get_object(object_name)

        if not obj.animation_data or not obj.animation_data.action:
            return {
                "success": True,
                "keyframes": {},
                "message": f"Object '{object_name}' has no keyframes.",
            }

        keyframes = {}
        for fcurve in obj.animation_data.action.fcurves:
            data_path = fcurve.data_path
            frames = [kp.co[0] for kp in fcurve.keyframe_points]
            keyframes[data_path] = frames

        return {
            "success": True,
            "keyframes": keyframes,
            "message": f"Retrieved keyframes for '{object_name}'",
        }

    def set_timeline_range(self, start_frame, end_frame, current_frame=None):
        """Set timeline range"""
        scene = bpy.context.scene
        scene.frame_start = start_frame
        scene.frame_end = end_frame

        if current_frame is not None:
            scene.frame_current = current_frame

        return {
            "success": True,
            "start": start_frame,
            "end": end_frame,
            "message": f"Timeline range set to {start_frame}-{end_frame}",
        }

    def play_animation(self, play=True):
        """Play or stop animation"""
        if play:
            bpy.ops.screen.animation_play()
        else:
            bpy.ops.screen.animation_cancel()

        return {
            "success": True,
            "playing": play,
            "message": f"Animation {'playing' if play else 'stopped'}",
        }

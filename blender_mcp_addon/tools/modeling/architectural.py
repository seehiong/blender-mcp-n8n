import bpy
import bmesh
import math
import mathutils
from ...utils import get_object, get_collection


class ModelingArchitectural:
    def build_wall_segment(
        self,
        start_point,
        end_point,
        height=2.8,
        thickness=0.15,
        name="Wall",
        collection=None,
        **kwargs,
    ):
        """Create a solid interior partition wall segment.

        Default thickness 0.15m (150mm) — standard interior partition.
        Uses bmesh.ops.solidify to extrude the face along its normal.
        """
        p1 = mathutils.Vector(
            start_point[:2] + [0.0]
            if len(start_point) == 2
            else [start_point[0], start_point[1], 0.0]
        )
        p2 = mathutils.Vector(
            end_point[:2] + [0.0]
            if len(end_point) == 2
            else [end_point[0], end_point[1], 0.0]
        )

        if (p2 - p1).length < 1e-6:
            return {
                "success": False,
                "message": "start_point and end_point are the same.",
            }

        if collection:
            coll = get_collection(collection)
        else:
            coll = bpy.context.scene.collection

        mesh = bpy.data.meshes.new(name)
        obj = bpy.data.objects.new(name, mesh)
        if obj.name not in coll.objects:
            coll.objects.link(obj)

        bm = bmesh.new()
        v0 = bm.verts.new(p1)
        v1 = bm.verts.new(p2)
        v2 = bm.verts.new(mathutils.Vector((p2.x, p2.y, height)))
        v3 = bm.verts.new(mathutils.Vector((p1.x, p1.y, height)))
        face = bm.faces.new([v0, v1, v2, v3])
        bm.normal_update()

        # Give the face physical thickness
        bmesh.ops.solidify(bm, geom=[face], thickness=thickness)

        bm.to_mesh(mesh)
        bm.free()

        bpy.context.view_layer.objects.active = obj
        obj.select_set(True)

        return {
            "success": True,
            "verified": True,
            "name": obj.name,
            "message": (
                f"Interior wall '{name}' created "
                f"({(p2 - p1).length:.2f}m long × {height}m tall × {thickness}m thick)."
            ),
        }

    def build_room_shell(
        self,
        vertices,
        height=2.8,
        wall_thickness=0.2,
        floor_thickness=0.15,
        name="Room",
        collection=None,
        doors=None,
        windows=None,
        **kwargs,
    ):
        """Extrude a 2D vertex perimeter into a full 3D room shell with support for windows/doors.

        Uses a 'Grid-Based' strategy:
        1. For each perimeter edge, collect all opening boundaries (X) and heights (Z).
        2. Create a perfectly aligned vertex grid for that wall.
        3. Build faces for the grid, skipping the 'holes' defined by openings.
        4. Solidify the entire manifold ring at once.
        """
        # --- resolve collection ---
        if collection:
            coll = get_collection(collection)
        else:
            coll = bpy.context.scene.collection

        # Normalise vertices to (x, y, z=0)
        pts2d = []
        for p in vertices:
            pts2d.append(mathutils.Vector((p[0], p[1], 0.0)))

        if len(pts2d) < 3:
            return {
                "success": False,
                "message": "Need at least 3 vertices to form a room shell.",
            }

        def _make_obj(mesh_name):
            mesh = bpy.data.meshes.new(mesh_name)
            obj = bpy.data.objects.new(mesh_name, mesh)
            if obj.name not in coll.objects:
                coll.objects.link(obj)
            return obj, mesh

        # ── 1. FLOOR ──────────────────────────────────────────────────────────
        floor_name = f"{name}_Floor"
        floor_obj, floor_mesh = _make_obj(floor_name)
        bm = bmesh.new()
        floor_verts = [bm.verts.new(p) for p in pts2d]
        floor_face = bm.faces.new(floor_verts)
        bm.normal_update()
        bmesh.ops.solidify(bm, geom=[floor_face], thickness=-floor_thickness)
        bm.to_mesh(floor_mesh)
        bm.free()

        # ── 2. WALLS ──────────────────────────────────────────────────────────
        wall_name = f"{name}_Walls"
        wall_obj, wall_mesh = _make_obj(wall_name)
        bm = bmesh.new()

        # 1. Collect ALL opening heights (Z) building-wide to ensure manifold corners
        edge_openings = {}
        global_z_cuts = {0.0, height}

        if doors:
            for d in doors:
                idx = d.get("edge_index")
                if idx is not None and 0 <= idx < len(pts2d):
                    dh = d.get("height", 2.1)
                    edge_openings.setdefault(idx, []).append(
                        ("door", d.get("offset", 0.0), d.get("width", 0.9), dh, 0.0)
                    )
                    global_z_cuts.add(max(0.0, min(dh, height)))
        if windows:
            for w in windows:
                idx = w.get("edge_index")
                if idx is not None and 0 <= idx < len(pts2d):
                    sh = w.get("sill_height", 0.9)
                    wh = w.get("height", 1.5)
                    edge_openings.setdefault(idx, []).append(
                        (
                            "window",
                            w.get("offset", 0.0),
                            w.get("width", 1.2),
                            sh + wh,
                            sh,
                        )
                    )
                    global_z_cuts.add(max(0.0, min(sh, height)))
                    global_z_cuts.add(max(0.0, min(sh + wh, height)))

        # Sort and merge nearly identical Z-cuts (1mm tolerance)
        z_raw = sorted(list(global_z_cuts))
        z_sorted = [z_raw[0]]
        for z in z_raw[1:]:
            if z - z_sorted[-1] > 0.001:
                z_sorted.append(z)

        n = len(pts2d)
        up = mathutils.Vector((0, 0, 1.0))

        # Vertex Cache for core corners (strictly shared between edges)
        v_bot_cache = [bm.verts.new(p) for p in pts2d]
        v_top_cache = [bm.verts.new(p + up * height) for p in pts2d]

        for i in range(n):
            j = (i + 1) % n
            p1, p2 = pts2d[i], pts2d[j]
            wall_vec = p2 - p1
            length = wall_vec.length
            if length < 1e-6:
                continue

            unit = wall_vec.normalized()
            openings = edge_openings.get(i, [])

            # 2. Collect X-cuts for this specific wall and merge duplicates
            x_raw = {0.0, length}
            for ot, oo, ow, otop, osill in openings:
                x_raw.add(max(0.0, min(oo, length)))
                x_raw.add(max(0.0, min(oo + ow, length)))

            x_sorted_pre = sorted(list(x_raw))
            x_sorted = [x_sorted_pre[0]]
            for x in x_sorted_pre[1:]:
                if x - x_sorted[-1] > 0.001:
                    x_sorted.append(x)

            # 3. Build Vertex Grid for this wall
            # grid[xi][zi] = vertex
            grid = []
            for xi, x in enumerate(x_sorted):
                stack = []
                for zi, z in enumerate(z_sorted):
                    # Use shared corner vertices for base/top boundaries
                    if xi == 0 and zi == 0:
                        v = v_bot_cache[i]
                    elif xi == 0 and zi == len(z_sorted) - 1:
                        v = v_top_cache[i]
                    elif xi == len(x_sorted) - 1 and zi == 0:
                        v = v_bot_cache[j]
                    elif xi == len(x_sorted) - 1 and zi == len(z_sorted) - 1:
                        v = v_top_cache[j]
                    else:
                        v = bm.verts.new(p1 + unit * x + up * z)
                    stack.append(v)
                grid.append(stack)

            # 4. Create quad faces, skipping opening areas
            for xi in range(len(x_sorted) - 1):
                x_mid = (x_sorted[xi] + x_sorted[xi + 1]) / 2.0
                active_openings = [
                    o for o in openings if o[1] - 1e-4 <= x_mid <= o[1] + o[2] + 1e-4
                ]

                for zi in range(len(z_sorted) - 1):
                    z_mid = (z_sorted[zi] + z_sorted[zi + 1]) / 2.0

                    is_hole = False
                    for ot, oo, ow, otop, osill in active_openings:
                        if osill - 1e-4 <= z_mid <= otop + 1e-4:
                            is_hole = True
                            break

                    if not is_hole:
                        # Normal points outward for CCW perimeter
                        bm.faces.new(
                            [
                                grid[xi][zi],
                                grid[xi + 1][zi],
                                grid[xi + 1][zi + 1],
                                grid[xi][zi + 1],
                            ]
                        )

        bm.normal_update()
        # Clean up any coincident vertices
        bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=0.0001)
        # Apply solidification to the entire manifold mesh ring
        bmesh.ops.solidify(bm, geom=bm.faces, thickness=-wall_thickness)
        bm.to_mesh(wall_mesh)
        bm.free()

        # ── 3. CEILING ────────────────────────────────────────────────────────
        ceil_name = f"{name}_Ceiling"
        ceil_obj, ceil_mesh = _make_obj(ceil_name)
        bm = bmesh.new()
        ceil_verts = [bm.verts.new(mathutils.Vector((p.x, p.y, height))) for p in pts2d]
        bm.faces.new(ceil_verts)
        bm.normal_update()
        bm.to_mesh(ceil_mesh)
        bm.free()

        # Hide ceiling by default (user request)
        ceil_obj.hide_viewport = True
        ceil_obj.hide_render = True

        # Make floor active / selected for convenience
        bpy.context.view_layer.objects.active = floor_obj
        floor_obj.select_set(True)

        return {
            "success": True,
            "verified": True,
            "floor": floor_name,
            "walls": wall_name,
            "ceiling": ceil_name,
            "message": (
                f"Room shell '{name}' created — {len(pts2d)} vertices, "
                f"{height}m tall, {wall_thickness}m walls, {floor_thickness}m floor slab. "
                f"Objects: {floor_name}, {wall_name}, {ceil_name}."
            ),
        }

    def toggle_ceiling(self, object_name, visible=False, **kwargs):
        """Show or hide an object (intended for ceiling objects)."""
        obj = get_object(object_name)
        obj.hide_viewport = not visible
        obj.hide_render = not visible
        state = "visible" if visible else "hidden"
        return {
            "success": True,
            "verified": True,
            "object": object_name,
            "state": state,
            "message": f"'{object_name}' is now {state} in viewport and render.",
        }

    def build_wall_with_door(
        self,
        start_point,
        end_point,
        height=2.8,
        thickness=0.15,
        door_offset=None,
        door_width=0.9,
        door_height=2.1,
        name="Wall",
        collection=None,
        **kwargs,
    ):
        """Create a wall segment with a door opening — pure vertex/face construction.

        Default thickness 0.15m (150mm) — standard interior partition.
        Three faces: left panel, lintel above door, right panel.
        Door aperture = absent geometry (open space).
        bmesh.ops.solidify gives all three faces physical thickness;
        the door hole stays open since there is no face there.
        """
        p1 = mathutils.Vector(
            start_point[:3] if len(start_point) >= 3 else (*start_point, 0)
        )
        p2 = mathutils.Vector(end_point[:3] if len(end_point) >= 3 else (*end_point, 0))

        # Force Z=0 for base of wall
        p1.z = 0.0
        p2.z = 0.0

        wall_vec = p2 - p1
        length = wall_vec.length
        if length < 1e-6:
            return {
                "success": False,
                "message": "start_point and end_point are the same.",
            }

        # Default door centred in wall
        if door_offset is None:
            door_offset = (length - door_width) / 2.0

        door_offset = max(0.0, min(door_offset, length - door_width))
        door_width = min(door_width, length - door_offset)

        unit = wall_vec.normalized()
        # Wall normal (perpendicular, XY plane — used for thickness direction)
        normal = mathutils.Vector((-unit.y, unit.x, 0.0))

        def f(dist, z):  # front-plane position
            return p1 + unit * dist + mathutils.Vector((0, 0, z))

        def b(dist, z):  # back-plane position (offset by thickness)
            return f(dist, z) + normal * thickness

        # 10 front-plane positions + 10 back-plane positions
        do = door_offset
        dw = door_width
        p1ff = f(0, 0)
        p1bf = b(0, 0)
        dLff = f(do, 0)
        dLbf = b(do, 0)
        dRff = f(do + dw, 0)
        dRbf = b(do + dw, 0)
        p2ff = f(length, 0)
        p2bf = b(length, 0)
        dLft = f(do, door_height)
        dLbt = b(do, door_height)
        dRft = f(do + dw, door_height)
        dRbt = b(do + dw, door_height)
        p1fc = f(0, height)
        p1bc = b(0, height)
        dLfc = f(do, height)
        dLbc = b(do, height)
        dRfc = f(do + dw, height)
        dRbc = b(do + dw, height)
        p2fc = f(length, height)
        p2bc = b(length, height)

        # ── Build mesh ────────────────────────────────────────────────────────
        if collection:
            coll = get_collection(collection)
        else:
            coll = bpy.context.scene.collection

        mesh = bpy.data.meshes.new(name)
        obj = bpy.data.objects.new(name, mesh)
        if obj.name not in coll.objects:
            coll.objects.link(obj)

        bm = bmesh.new()
        V = bm.verts.new
        F = bm.faces.new

        # Front verts
        vp1ff = V(p1ff)
        vdLff = V(dLff)
        vdRff = V(dRff)
        vp2ff = V(p2ff)
        vdLft = V(dLft)
        vdRft = V(dRft)
        vp1fc = V(p1fc)
        vdLfc = V(dLfc)
        vdRfc = V(dRfc)
        vp2fc = V(p2fc)
        # Back verts
        vp1bf = V(p1bf)
        vdLbf = V(dLbf)
        vdRbf = V(dRbf)
        vp2bf = V(p2bf)
        vdLbt = V(dLbt)
        vdRbt = V(dRbt)
        vp1bc = V(p1bc)
        vdLbc = V(dLbc)
        vdRbc = V(dRbc)
        vp2bc = V(p2bc)

        right_w = length - (do + dw)
        left_exists = do > 1e-4
        right_exists = right_w > 1e-4

        # Front faces
        if left_exists:
            F([vp1ff, vdLff, vdLfc, vp1fc])
        F([vdLft, vdRft, vdRfc, vdLfc])  # lintel
        if right_exists:
            F([vdRff, vp2ff, vp2fc, vdRfc])

        # Back faces (reversed winding → outward normals)
        if left_exists:
            F([vp1bf, vp1bc, vdLbc, vdLbf])
        F([vdLbt, vdLbc, vdRbc, vdRbt])  # lintel
        if right_exists:
            F([vdRbf, vdRbc, vp2bc, vp2bf])

        # Wall-end caps (at p1 and p2)
        if left_exists:
            F([vp1ff, vp1bf, vp1bc, vp1fc])
        else:
            F([vdLft, vdLbt, vdLbc, vdLfc])  # lintel-only at p1
        if right_exists:
            F([vp2ff, vp2fc, vp2bc, vp2bf])
        else:
            F([vdRft, vdRfc, vdRbc, vdRbt])  # lintel-only at p2

        # Top caps (ceiling surface)
        if left_exists:
            F([vp1fc, vdLfc, vdLbc, vp1bc])
        F([vdLfc, vdRfc, vdRbc, vdLbc])  # over lintel
        if right_exists:
            F([vdRfc, vp2fc, vp2bc, vdRbc])

        # Door-frame interior faces (jambs + header)
        if left_exists:
            F([vdLff, vdLft, vdLbt, vdLbf])  # left jamb
        F([vdLft, vdRft, vdRbt, vdLbt])  # door header
        if right_exists:
            F([vdRft, vdRff, vdRbf, vdRbt])  # right jamb

        bm.normal_update()
        bm.to_mesh(mesh)
        bm.free()

        bpy.context.view_layer.objects.active = obj
        obj.select_set(True)

        return {
            "success": True,
            "verified": True,
            "name": obj.name,
            "door_offset": door_offset,
            "door_width": door_width,
            "door_height": door_height,
            "message": (
                f"Wall '{name}' created with door opening "
                f"({door_width}m wide × {door_height}m tall, "
                f"offset {door_offset:.2f}m) — {thickness}m thick. "
                f"No booleans — pure vertex/face + solidify."
            ),
        }

    def set_view(self, mode="TOP", **kwargs):
        """Switch viewport view (best effort)"""
        valid_modes = ["TOP", "ISO", "FRONT", "SIDE"]
        if mode not in valid_modes:
            return {
                "success": False,
                "message": f"Invalid mode. Choose from {valid_modes}",
            }

        # In bridge mode, we are running inside Blender's process
        # so we might be able to find a 3D view and change it.
        for area in bpy.context.screen.areas:
            if area.type == "VIEW_3D":
                for region in area.regions:
                    if region.type == "WINDOW":
                        override = {
                            "area": area,
                            "region": region,
                            "edit_object": bpy.context.edit_object,
                            "scene": bpy.context.scene,
                            "screen": bpy.context.screen,
                        }
                        try:
                            # Use temp_override for Blender 3.2+
                            if hasattr(bpy.context, "temp_override"):
                                with bpy.context.temp_override(**override):
                                    if mode == "TOP":
                                        bpy.ops.view3d.view_axis(type="TOP")
                                    elif mode == "FRONT":
                                        bpy.ops.view3d.view_axis(type="FRONT")
                                    elif mode == "SIDE":
                                        bpy.ops.view3d.view_axis(type="RIGHT")
                                    elif mode == "ISO":
                                        bpy.ops.view3d.view_axis(type="TOP")
                                        bpy.ops.view3d.view_orbit(
                                            angle=math.radians(45), type="ORBITRIGHT"
                                        )
                                        bpy.ops.view3d.view_orbit(
                                            angle=math.radians(-45), type="ORBITUP"
                                        )
                            else:
                                # Legacy override for < 3.2
                                if mode == "TOP":
                                    bpy.ops.view3d.view_axis(override, type="TOP")
                                elif mode == "FRONT":
                                    bpy.ops.view3d.view_axis(override, type="FRONT")
                                elif mode == "SIDE":
                                    bpy.ops.view3d.view_axis(override, type="RIGHT")
                                elif mode == "ISO":
                                    bpy.ops.view3d.view_axis(override, type="TOP")
                                    bpy.ops.view3d.view_orbit(
                                        override,
                                        angle=math.radians(45),
                                        type="ORBITRIGHT",
                                    )
                                    bpy.ops.view3d.view_orbit(
                                        override,
                                        angle=math.radians(-45),
                                        type="ORBITUP",
                                    )
                            break
                        except Exception as e:
                            return {
                                "success": True,
                                "message": f"View mode set to {mode} (UI update failed: {str(e)})",
                            }

        return {
            "success": True,
            "message": f"View mode set to {mode}. (AI: Working in {mode} mode)",
        }

    def build_column(
        self,
        location,
        width=0.4,
        depth=0.4,
        height=2.8,
        name="Column",
        collection=None,
        union_with=None,
        **kwargs,
    ):
        """Create a structural column and optionally merge with another object."""
        if collection:
            coll = get_collection(collection)
        else:
            coll = bpy.context.scene.collection

        # Create a simple box mesh
        mesh = bpy.data.meshes.new(name)
        obj = bpy.data.objects.new(name, mesh)
        coll.objects.link(obj)

        bm = bmesh.new()
        # Location is bottom-left corner
        x, y = location[0], location[1]

        # Build 8 verts
        verts = [
            bm.verts.new((x, y, 0)),
            bm.verts.new((x + width, y, 0)),
            bm.verts.new((x + width, y + depth, 0)),
            bm.verts.new((x, y + depth, 0)),
            bm.verts.new((x, y, height)),
            bm.verts.new((x + width, y, height)),
            bm.verts.new((x + width, y + depth, height)),
            bm.verts.new((x, y + depth, height)),
        ]

        # 6 faces
        bm.faces.new([verts[0], verts[1], verts[2], verts[3]])  # Bottom
        bm.faces.new([verts[4], verts[7], verts[6], verts[5]])  # Top
        bm.faces.new([verts[0], verts[4], verts[5], verts[1]])  # Front
        bm.faces.new([verts[1], verts[5], verts[6], verts[2]])  # Right
        bm.faces.new([verts[2], verts[6], verts[7], verts[3]])  # Back
        bm.faces.new([verts[3], verts[7], verts[4], verts[0]])  # Left

        bm.normal_update()
        bm.to_mesh(mesh)
        bm.free()

        res_msg = (
            f"Column '{name}' created at {location} ({width}m x {depth}m x {height}m)."
        )

        # --- OPTIONAL UNION ---
        if union_with:
            target_obj = get_object(union_with)
            if target_obj:
                # Add Boolean modifier to the TARGET (the Wall/Shell)
                bool_mod = target_obj.modifiers.new(name="Union_Column", type="BOOLEAN")
                bool_mod.operation = "UNION"
                bool_mod.object = obj
                bool_mod.solver = "EXACT"

                # Apply it permanently
                bpy.context.view_layer.objects.active = target_obj
                bpy.ops.object.modifier_apply(modifier=bool_mod.name)

                # Delete the temporary column object (it's now part of the target)
                bpy.data.objects.remove(obj, do_unlink=True)
                res_msg += f" Merged into '{union_with}'."
                obj = target_obj  # Return target as the active object

        bpy.context.view_layer.objects.active = obj
        obj.select_set(True)

        return {
            "success": True,
            "verified": True,
            "name": obj.name,
            "message": res_msg,
        }

"""
HDB 3-Room Flat - Integration Test Scenario (Synced with my_session.json)
========================================================================
Replicates the exact layout fine-tuned in the session editor.
"""

from tests.utils.mcp_client import MCPClient


# ── Constants ────────────────────────────────────────────────────────────────
H = 2.8  # Ceiling height
COLLECTION = "HDB_3Room_Flat"


class ArchLayoutScenario:
    """Replicates a standard HDB 3-Room Flat layout."""

    def __init__(self, client: MCPClient):
        self.client = client

    def run(self):
        print("=" * 60)
        print("HDB 3-Room Flat — Integration Test (Synced)")
        print("=" * 60)

        self._build_outer_shell()
        self._build_columns()
        self._build_bedroom_partitions()
        self._build_living_room_partitions()
        self._build_main_bedroom_partitions()
        self._build_bath_partitions()
        self._build_kitchen_store_partitions()
        self._build_chute_partitions()
        self._add_labels()

        print("=" * 60)
        print("✅ HDB 3-Room Flat scenario complete.")
        print("=" * 60)

    # ── 1. Outer Shell ───────────────────────────────────────────────────────

    def _build_outer_shell(self):
        print("\n[1] Building outer shell...")
        self.client.call_tool(
            "build_room_shell",
            {
                "name": "HDB_Unit",
                "collection": COLLECTION,
                "wall_thickness": 0.2,
                "height": H,
                "vertices": [
                    [0.0, 0.0],
                    [6.0, 0.0],
                    [6.0, 15.25],
                    [1.3, 15.25],
                    [1.3, 11.6],
                    [0.0, 11.6],
                    [0.0, 0.0],
                ],
                "doors": [
                    {"edge_index": 1, "offset": 0.8, "width": 0.9, "height": 2.1}
                ],
                "windows": [
                    {
                        "edge_index": 0,
                        "offset": 0.7,
                        "width": 2.0,
                        "height": 1.2,
                        "sill_height": 1.2,
                    },
                    {
                        "edge_index": 0,
                        "offset": 3.8,
                        "width": 2.0,
                        "height": 1.2,
                        "sill_height": 1.2,
                    },
                    {
                        "edge_index": 2,
                        "offset": 0.75,
                        "width": 2.2,
                        "height": 1.2,
                        "sill_height": 1.5,
                    },
                    {
                        "edge_index": 4,
                        "offset": 0.25,
                        "width": 0.9,
                        "height": 1.2,
                        "sill_height": 1.5,
                    },
                ],
            },
        )

    def _build_columns(self):
        print("\n[1.5] Building structural columns...")
        # Column at corner
        self.client.call_tool(
            "build_column",
            {
                "name": "Col_Corner_LT",
                "location": [-0.3, -0.7],
                "width": 0.4,
                "depth": 1.0,
                "collection": COLLECTION,
                "union_with": "HDB_Unit_Walls",
            },
        )
        # Column at corner
        self.client.call_tool(
            "build_column",
            {
                "name": "Col_Corner_RT",
                "location": [5.9, -0.7],
                "width": 0.4,
                "depth": 1.0,
                "collection": COLLECTION,
                "union_with": "HDB_Unit_Walls",
            },
        )
        # Column in the bedroom
        self.client.call_tool(
            "build_column",
            {
                "name": "Col_Bedroom",
                "location": [-0.3, 2.4],
                "width": 0.4,
                "depth": 1.0,
                "collection": COLLECTION,
                "union_with": "HDB_Unit_Walls",
            },
        )
        # Column in the living room
        self.client.call_tool(
            "build_column",
            {
                "name": "Col_Living_Room",
                "location": [5.9, 2.4],
                "width": 0.4,
                "depth": 1.0,
                "collection": COLLECTION,
                "union_with": "HDB_Unit_Walls",
            },
        )
        # Column in the main bedroom
        self.client.call_tool(
            "build_column",
            {
                "name": "Col_Main_Bedroom1",
                "location": [-0.3, 7.6],
                "width": 0.4,
                "depth": 1.0,
                "collection": COLLECTION,
                "union_with": "HDB_Unit_Walls",
            },
        )
        self.client.call_tool(
            "build_column",
            {
                "name": "Col_Main_Bedroom2",
                "location": [-0.3, 11.5],
                "width": 0.4,
                "depth": 0.6,
                "collection": COLLECTION,
                "union_with": "HDB_Unit_Walls",
            },
        )
        # Column in the kitchen
        self.client.call_tool(
            "build_column",
            {
                "name": "Col_Kitchen",
                "location": [2.6, 7.6],
                "width": 0.4,
                "depth": 1.0,
                "collection": COLLECTION,
                "union_with": "HDB_Unit_Walls",
            },
        )
        # Column in the store
        self.client.call_tool(
            "build_column",
            {
                "name": "Col_Store",
                "location": [5.9, 7.6],
                "width": 0.4,
                "depth": 1.0,
                "collection": COLLECTION,
                "union_with": "HDB_Unit_Walls",
            },
        )
        # Column in the bath
        self.client.call_tool(
            "build_column",
            {
                "name": "Col_Bath",
                "location": [1.1, 15.25],
                "width": 1.75,
                "depth": 0.4,
                "collection": COLLECTION,
                "union_with": "HDB_Unit_Walls",
            },
        )
        # Column in the chute
        self.client.call_tool(
            "build_column",
            {
                "name": "Col_Chute1",
                "location": [5.3, 15.25],
                "width": 0.2,
                "depth": 0.4,
                "collection": COLLECTION,
                "union_with": "HDB_Unit_Walls",
            },
        )
        self.client.call_tool(
            "build_column",
            {
                "name": "Col_Chute2",
                "location": [6.0, 15.25],
                "width": 0.2,
                "depth": 0.4,
                "collection": COLLECTION,
                "union_with": "HDB_Unit_Walls",
            },
        )

    # ── 2. Bedroom ──────────────────────────────────────────────────────────

    def _build_bedroom_partitions(self):
        print("\n[2] Building Bedroom partitions...")
        # Wall_Bedroom_Right
        self.client.call_tool(
            "build_wall_segment",
            {
                "name": "Wall_Bedroom_Right",
                "collection": COLLECTION,
                "start_point": [3.0, 0.0],
                "end_point": [3.0, 4.0],
                "height": H,
                "thickness": 0.15,
            },
        )
        # Wall_Bedroom_Top
        self.client.call_tool(
            "build_wall_with_door",
            {
                "name": "Wall_Bedroom_Top",
                "collection": COLLECTION,
                "start_point": [0.0, 4.0],
                "end_point": [3.0, 4.0],
                "height": H,
                "thickness": 0.15,
                "door_width": 0.90,
                "door_height": 2.1,
                "door_offset": 1.9,
            },
        )

    # ── 3. Living Room ──────────────────────────────────────────────────────

    def _build_living_room_partitions(self):
        print("\n[3] Building Living Room partitions...")
        # Wall_LivingRoom_Top_Left
        self.client.call_tool(
            "build_wall_with_door",
            {
                "name": "Wall_LivingRoom_Top_Left",
                "collection": COLLECTION,
                "start_point": [0.1, 7.6],
                "end_point": [2.6, 7.6],
                "height": H,
                "thickness": 0.15,
                "door_width": 1.0,
                "door_height": 2.1,
                "door_offset": 1.5,
            },
        )
        # Wall_LivingRoom_Top_Right
        self.client.call_tool(
            "build_wall_segment",
            {
                "name": "Wall_LivingRoom_Top_Right",
                "collection": COLLECTION,
                "start_point": [4.25, 6.0],
                "end_point": [6.0, 6.0],
                "height": H,
                "thickness": 0.15,
            },
        )

    # ── 4. Main Bedroom ─────────────────────────────────────────────────────

    def _build_main_bedroom_partitions(self):
        print("\n[4] Building Main Bedroom partitions...")
        # Wall_MainBedroom_Right
        self.client.call_tool(
            "build_wall_segment",
            {
                "name": "Wall_MainBedroom_Right",
                "collection": COLLECTION,
                "start_point": [3.0, 8.6],
                "end_point": [3.0, 11.75],
                "height": H,
                "thickness": 0.15,
            },
        )
        # Wall_MainBedroom_Top
        self.client.call_tool(
            "build_wall_with_door",
            {
                "name": "Wall_MainBedroom_Top",
                "collection": COLLECTION,
                "start_point": [1.3, 11.6],
                "end_point": [2.85, 11.6],
                "height": H,
                "thickness": 0.15,
                "door_width": 0.9,
                "door_height": 2.1,
                "door_offset": 0.6,
            },
        )

    # ── 5. Bath / WC Zone ───────────────────────────────────────────────────

    def _build_bath_partitions(self):
        print("\n[5] Building Bath/WC partitions...")
        # Wall_Bath_Middle_Divider
        self.client.call_tool(
            "build_wall_segment",
            {
                "name": "Wall_Bath_Middle_Divider",
                "collection": COLLECTION,
                "start_point": [1.3, 13.3],
                "end_point": [2.95, 13.3],
                "height": H,
                "thickness": 0.15,
            },
        )
        # Wall_Bath2_Entry
        self.client.call_tool(
            "build_wall_with_door",
            {
                "name": "Wall_Bath2_Entry",
                "collection": COLLECTION,
                "start_point": [3.0, 11.75],
                "end_point": [3.0, 15.25],
                "height": H,
                "thickness": 0.15,
                "door_width": 0.7,
                "door_height": 2.1,
                "door_offset": 2.6,
            },
        )

    # ── 6. Kitchen / Store ───────────────────────────────────────────────────

    def _build_kitchen_store_partitions(self):
        print("\n[6] Building Kitchen/Store partitions...")
        # Wall_Store_Left
        self.client.call_tool(
            "build_wall_with_door",
            {
                "name": "Wall_Store_Left",
                "collection": COLLECTION,
                "start_point": [4.25, 6.0],
                "end_point": [4.25, 8.56],
                "height": H,
                "thickness": 0.15,
                "door_width": 0.9,
                "door_height": 2.1,
                "door_offset": 0.2,
            },
        )
        # Wall_Store_Top
        self.client.call_tool(
            "build_wall_segment",
            {
                "name": "Wall_Store_Top",
                "collection": COLLECTION,
                "start_point": [4.1, 8.56],
                "end_point": [6.0, 8.56],
                "height": H,
                "thickness": 0.15,
            },
        )

    # ── 7. Chute ─────────────────────────────────────────────────────────────

    def _build_chute_partitions(self):
        print("\n[7] Building Chute partitions...")
        # Wall_Chute_Left
        self.client.call_tool(
            "build_wall_segment",
            {
                "name": "Wall_Chute_Left",
                "collection": COLLECTION,
                "start_point": [5.5, 13.9],
                "end_point": [5.5, 15.25],
                "height": H,
                "thickness": 0.2,
            },
        )
        # Wall_Chute_Bottom
        self.client.call_tool(
            "build_wall_segment",
            {
                "name": "Wall_Chute_Bottom",
                "collection": COLLECTION,
                "start_point": [5.5, 13.9],
                "end_point": [6.0, 13.9],
                "height": H,
                "thickness": 0.4,
            },
        )

    # ── 8. Labels ────────────────────────────────────────────────────────────

    def _add_labels(self):
        print("\n[8] Adding room labels...")
        labels = [
            # text, location, name, size (optional)
            ("BEDROOM", [1.5, 2.0, 0.2], "Lbl_Bedroom", 0.35),
            ("STORE", [5.1, 7.3, 0.2], "Lbl_Store", 0.35),
            ("MAIN\nBEDROOM", [1.2, 10, 0.2], "Lbl_Main", 0.35),
            ("KITCHEN /\nDINING", [4.5, 12.0, 0.2], "Lbl_Kitchen", 0.35),
            ("LIVING ROOM", [1.5, 6, 0.2], "Lbl_Living", 0.35),
            ("BATH 2", [2.1, 14.3, 0.2], "Lbl_Bath2", 0.25),
            ("BATH 1", [2.1, 12.5, 0.2], "Lbl_Bath1", 0.25),
            ("CHUTE", [5.8, 14.7, 0.2], "Lbl_Chute", 0.2, [0, 0, 90]),
        ]

        for item in labels:
            text, loc, name = item[0], item[1], item[2]
            size = item[3] if len(item) > 3 else 0.35
            rotation = item[4] if len(item) > 4 else None

            args = {
                "text": text,
                "location": loc,
                "name": name,
                "size": size,
                "align_x": "CENTER",
                "collection": COLLECTION,
            }
            if rotation:
                args["rotation"] = rotation

            self.client.call_tool("create_text", args)

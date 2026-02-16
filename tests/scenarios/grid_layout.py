from tests.utils.mcp_client import MCPClient
from tests.scenarios.modules.row_primitives import create_primitives_row
from tests.scenarios.modules.row_modifiers import create_modifiers_row
from tests.scenarios.modules.row_collections import create_collections_row
from tests.scenarios.modules.row_operators import create_operators_row
from tests.scenarios.modules.row_transforms import create_transforms_row


class GridLayoutScenario:
    def __init__(self, client: MCPClient):
        self.client = client

    def run(self, module: str = None):
        print(f"Starting Grid Layout Scenario (Modular) - Module: {module or 'ALL'}...")

        if not module or module == "primitives":
            # Row 1: Primitives (Y=0)
            self.client.call_tool(
                "create_text",
                {
                    "text": "Primitives",
                    "location": [-5.0, 0.0, 0.0],
                    "name": "Label_Primitives",
                    "size": 1.0,
                    "align_x": "RIGHT",
                },
            )
            create_primitives_row(self.client, y_offset=0.0)

        if not module or module == "modifiers":
            # Row 2: Modifiers & Operations (Y=10)
            self.client.call_tool(
                "create_text",
                {
                    "text": "Modifiers",
                    "location": [-5.0, 10.0, 0.0],
                    "name": "Label_Modifiers",
                    "size": 1.0,
                    "align_x": "RIGHT",
                },
            )
            create_modifiers_row(self.client, y_offset=10.0)

        if not module or module == "collections":
            # Row 3: Collections (Y=20)
            self.client.call_tool(
                "create_text",
                {
                    "text": "Collections",
                    "location": [-5.0, 20.0, 0.0],
                    "name": "Label_Collections",
                    "size": 1.0,
                    "align_x": "RIGHT",
                },
            )
            create_collections_row(self.client, y_offset=20.0)

        if not module or module == "operators":
            # Row 4: Operators (Y=30)
            self.client.call_tool(
                "create_text",
                {
                    "text": "Operators",
                    "location": [-5.0, 30.0, 0.0],
                    "name": "Label_Operators",
                    "size": 1.0,
                    "align_x": "RIGHT",
                },
            )
            create_operators_row(self.client, y_offset=30.0)

        if not module or module == "transforms":
            # Row 5: Transforms (Y=40)
            self.client.call_tool(
                "create_text",
                {
                    "text": "Transforms",
                    "location": [-5.0, 40.0, 0.0],
                    "name": "Label_Transforms",
                    "size": 1.0,
                    "align_x": "RIGHT",
                },
            )
            create_transforms_row(self.client, y_offset=40.0)

        print("Grid Layout Scenario Completed.")

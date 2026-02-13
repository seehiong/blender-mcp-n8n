from .primitives import ModelingPrimitives
from .modifiers import ModelingModifiers
from .transforms import ModelingTransforms
from .selection import ModelingSelection
from .operators import ModelingOperators


class ModelingTools(
    ModelingPrimitives,
    ModelingModifiers,
    ModelingTransforms,
    ModelingSelection,
    ModelingOperators,
):
    """Refactored Modeling Tools for Blender MCP"""

    pass

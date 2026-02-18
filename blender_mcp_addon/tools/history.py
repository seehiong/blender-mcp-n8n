import bpy


class HistoryTools:
    def undo_action(self):
        try:
            bpy.ops.ed.undo()
            return {"status": "success", "message": "Undo successful"}
        except Exception as e:
            return {"status": "error", "message": f"Undo failed: {str(e)}"}

    def redo_action(self):
        try:
            bpy.ops.ed.redo()
            return {"status": "success", "message": "Redo successful"}
        except Exception as e:
            return {"status": "error", "message": f"Redo failed: {str(e)}"}

# Session Editor

This directory contains a static web application for viewing, editing, and sharing Blender MCP recordings (`session.json`).

## Features

- **Load Sessions**: Load `session.json` files recorded by the Blender MCP server.
- **Metadata Editing**: Update session name, AI model, and description.
- **Visual Playback**:
    - **▶ Play Session**: Execute all commands in sequence.
    - **⏹ Stop**: Pause playback.
    - **🗑 Clear Scene**: Instantly delete all objects in the Blender scene to start fresh.
    - **↺ Reset State**: Re-enable all "Run" buttons and clear success indicators without modifying the scene.
    - **Note**: This editor focuses on *sequencing* and *control*. Please keep Blender open side-by-side to watch the magic happen! 🪄
- **Command Control**:
    - **Run Individual**: Execute specific tools manually.
    - **Success State**: Commands turn green and show "✓ Done" upon successful execution.
    - **Edit Arguments**: Modify tool parameters directly in the JSON editor cards.
    - **Reorder/Delete**: Rearrange or remove commands to refine the workflow.
- **Export JSON**: Save your modified session to a new file.

## How to Use

1.  **Open Editor**: Open `index.html` in your web browser (or via `http://localhost:8000/editor/` if running the server).
2.  **Load Recording**: Drag and drop a `session.json` file or use the "Load Session" button.
3.  **Review & Edit**:
    *   Check command arguments and descriptions.
    *   Use **🗑 Clear Scene** to ensure Blender is empty before running.
4.  **Playback**:
    *   Click **▶ Play Session** to run the full workflow.
    *   Or click **▶ Run** on individual cards to step through manually.
    *   Successful commands will turn **Green** and lock to prevent accidental re-running.
5.  **Reset**: Use **↺ Reset State** to unlock buttons if you need to re-run a command (e.g., after changing arguments).

## Sharing Recordings

If you want to share your work with the community, please follow the guide in the [community](../community/README.md) folder.

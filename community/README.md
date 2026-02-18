# Community Projects

Welcome to the Blender MCP community! This folder is a space for users to share their creative works, recorded sessions, and documentation.

> [!IMPORTANT]
> **Core Philosophy**: A session should replay successfully on a fresh Blender file. This ensures your contribution is portable and works for everyone.

## How to Share Your Project

Before uploading, you need to export a clean recording of your build. Follow this 3-step pipeline:

### 1) Record a Session

Start the MCP server in recording mode:

```bash
python -m src.main serve --record my_session.json --name "My Project"
```

Then build your scene using n8n or your AI agent as usual. Every modeling command will automatically be saved. When finished, stop the server — your `session.json` is ready.

> [!TIP]
> Record only the final successful build. Avoid recording failed experiments to keep sessions clean.

### 2. Clean the Recording (Recommended)

Large or messy sessions make playback slow for others. Use the built-in editor to tidy it:

1.  Open `session_editor/index.html` in your web browser.
2.  **Load** your `session.json`.
3.  **Delete** mistakes or unnecessary commands.
4.  **Export JSON** to save the cleaned file.

This keeps the community gallery fast and reliable.

### 3) Upload Your Project

Create a new folder in `community/` with the following structure:

```text
community/your_project/
├── README.md           # Instructions and documentation
├── session.json        # The cleaned MCP session
└── assets/
    └── images/        # screenshots, renders, etc.
```

Then open a **Pull Request** 🚀

---

## Scaling Up

As the community grows, we may transition from a folder-based structure to an indexed gallery (e.g., a database-backed catalog such as Firestore) to better showcase projects.
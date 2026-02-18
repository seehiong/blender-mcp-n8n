document.addEventListener('DOMContentLoaded', () => {
    const fileInput = document.getElementById('fileInput');
    const loadBtn = document.getElementById('loadBtn');
    const saveBtn = document.getElementById('saveBtn');
    const commandList = document.getElementById('commandList');
    const commandCount = document.getElementById('commandCount');
    const commandFilter = document.getElementById('commandFilter');
    const sessionName = document.getElementById('sessionName');
    const sessionModel = document.getElementById('sessionModel');
    const sessionCreatedAt = document.getElementById('sessionCreatedAt');
    const sessionDescription = document.getElementById('sessionDescription');
    const commandTemplate = document.getElementById('commandTemplate');
    const themeToggle = document.getElementById('themeToggle');
    const body = document.body;

    const connectionStatus = document.getElementById('connectionStatus');
    const undoBtn = document.getElementById('undoBtn');
    const redoBtn = document.getElementById('redoBtn');
    const playBtn = document.getElementById('playBtn');
    const stopBtn = document.getElementById('stopBtn');
    const clearSceneBtn = document.getElementById('clearSceneBtn');
    const resetStateBtn = document.getElementById('resetStateBtn');
    const playbackDelay = document.getElementById('playbackDelay');


    let currentSession = null;
    let lastMovedCommand = null;
    let isPlaying = false;
    let playbackTimeout = null;
    const executedCommands = new Set(); // tracks indices of successfully executed commands

    // Server API Configuration
    // If opened via file:// protocol, default to localhost:8000
    const API_BASE = (window.location.protocol === 'file:' || window.location.origin === 'null')
        ? 'http://localhost:8000'
        : window.location.origin;

    // --- Server Connection Logic ---

    async function checkConnection() {
        try {
            // GET the root endpoint — simple and always available if server is running
            const resp = await fetch(`${API_BASE}/`, { method: 'GET' });
            if (resp.ok) {
                connectionStatus.classList.add('connected');
                connectionStatus.classList.remove('error');
                connectionStatus.querySelector('.status-text').textContent = 'Connected';
                return true;
            }
        } catch (err) {
            connectionStatus.classList.remove('connected');
            connectionStatus.classList.add('error');
            connectionStatus.querySelector('.status-text').textContent = 'Offline';
        }
        return false;
    }

    // Poll for connection every 5 seconds
    setInterval(checkConnection, 5000);
    checkConnection();

    // --- Command Execution Logic ---

    async function runCommand(tool, args) {
        try {
            const response = await fetch(`${API_BASE}/mcp`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Accept': 'application/json, text/event-stream'
                },
                body: JSON.stringify({
                    jsonrpc: '2.0',
                    method: 'tools/call',
                    params: { name: tool, arguments: args },
                    id: Math.random().toString(36).substring(7)
                })
            });

            const text = await response.text();
            let data;
            try {
                data = JSON.parse(text);
            } catch {
                return { error: `Server returned non-JSON: ${text.substring(0, 200)}` };
            }

            // JSON-RPC response: { result: {...}, error: {...} }
            if (data.error) {
                const errMsg = typeof data.error === 'string'
                    ? data.error
                    : (data.error.message || JSON.stringify(data.error));
                return { error: errMsg };
            }
            // MCP wraps tool result in result.content[0].text
            if (data.result && data.result.content) {
                try {
                    return JSON.parse(data.result.content[0].text);
                } catch {
                    return { result: data.result.content[0].text };
                }
            }
            return data.result || data;
        } catch (err) {
            console.error('Command Execution Error:', err);
            const msg = err.message === 'Failed to fetch'
                ? 'Could not connect to Blender MCP Server. Please ensure the server is running.'
                : err.message;
            return { error: msg };
        }
    }



    // --- Playback Management ---

    async function playNext(index) {
        if (!isPlaying || index >= currentSession.commands.length) {
            stopPlayback();
            return;
        }

        const cards = document.querySelectorAll('.command-card');
        const card = cards[index];

        // Highlight active card
        cards.forEach(c => c.style.borderColor = '');
        card.style.borderColor = 'var(--accent-color)';
        card.scrollIntoView({ behavior: 'smooth', block: 'center' });

        const cmd = currentSession.commands[index];
        const res = await runCommand(cmd.tool, cmd.arguments);

        if (res.error) {
            card.style.borderColor = 'var(--danger-color)';
            const errMsg = typeof res.error === 'string' ? res.error : JSON.stringify(res.error);
            const shouldContinue = await modal.confirm(
                `Command Error #${index + 1}`,
                `Error: ${errMsg}\n\nDo you want to continue playback?`
            );
            if (!shouldContinue) {
                stopPlayback();
                return;
            }
        } else {
            card.style.borderColor = 'var(--success-color)';
            card.classList.add('cmd-executed');
        }

        const delay = parseInt(playbackDelay.value) || 500;
        playbackTimeout = setTimeout(() => playNext(index + 1), delay);
    }

    function startPlayback() {
        if (!currentSession || currentSession.commands.length === 0) return;
        isPlaying = true;
        playBtn.disabled = true;
        stopBtn.disabled = false;
        playNext(0);
    }

    function stopPlayback() {
        isPlaying = false;
        clearTimeout(playbackTimeout);
        playBtn.disabled = false;
        stopBtn.disabled = true;

        // Clear highlights
        document.querySelectorAll('.command-card').forEach(c => c.style.borderColor = '');
    }

    playBtn.addEventListener('click', startPlayback);
    stopBtn.addEventListener('click', stopPlayback);

    // --- Undo / Redo ---
    undoBtn.addEventListener('click', async () => {
        undoBtn.disabled = true;
        const res = await runCommand('undo', {});
        undoBtn.disabled = false;

        if (res.error) {
            modal.alert('Undo Failed', res.error.message || JSON.stringify(res.error));
        } else {
            // Optional: feedback notification
            console.log('Undo successful');
        }
    });

    redoBtn.addEventListener('click', async () => {
        redoBtn.disabled = true;
        const res = await runCommand('redo', {});
        redoBtn.disabled = false;

        if (res.error) {
            modal.alert('Redo Failed', res.error.message || JSON.stringify(res.error));
        } else {
            // Optional: feedback notification
            console.log('Redo successful');
        }
    });

    // --- Clear Scene ---
    clearSceneBtn.addEventListener('click', async () => {
        const confirmed = await modal.confirm(
            'Clear Scene',
            'This will delete ALL objects in the Blender scene. Are you sure?'
        );
        if (!confirmed) return;

        clearSceneBtn.disabled = true;
        clearSceneBtn.textContent = '...';
        const res = await runCommand('delete_object', { pattern: '*' });
        clearSceneBtn.disabled = false;
        clearSceneBtn.textContent = '🗑 Clear Scene';

        if (res.error) {
            const errMsg = typeof res.error === 'string' ? res.error : JSON.stringify(res.error);
            modal.alert('Clear Scene Error', errMsg);
        } else {
            // Re-enable all run buttons
            resetExecutionState();
            modal.alert('Scene Cleared', 'All objects deleted. Run buttons have been re-enabled.');
        }
    });

    // --- Reset State ---
    function resetExecutionState() {
        executedCommands.clear();
        document.querySelectorAll('.command-card').forEach(card => {
            card.classList.remove('cmd-executed');
            card.style.borderColor = '';
            const btn = card.querySelector('.run-cmd');
            if (btn) {
                btn.disabled = false;
                btn.textContent = '▶ Run';
            }
        });
    }

    resetStateBtn.addEventListener('click', () => {
        resetExecutionState();
    });

    // --- Modal System ---

    const modal = {
        overlay: document.getElementById('modalOverlay'),
        title: document.getElementById('modalTitle'),
        message: document.getElementById('modalMessage'),
        confirmBtn: document.getElementById('modalConfirm'),
        cancelBtn: document.getElementById('modalCancel'),
        closeBtn: document.getElementById('modalClose'),

        show(title, message, type = 'alert') {
            return new Promise((resolve) => {
                this.title.textContent = title;
                this.message.textContent = message;
                this.overlay.hidden = false;

                if (type === 'alert') {
                    this.cancelBtn.hidden = true;
                    this.confirmBtn.textContent = 'OK';
                } else {
                    this.cancelBtn.hidden = false;
                    this.confirmBtn.textContent = 'Yes, Continue';
                    this.cancelBtn.textContent = 'Stop All';
                }

                const cleanup = (value) => {
                    this.overlay.hidden = true;
                    this.confirmBtn.onclick = null;
                    this.cancelBtn.onclick = null;
                    this.closeBtn.onclick = null;
                    resolve(value);
                };

                this.confirmBtn.onclick = () => cleanup(true);
                this.cancelBtn.onclick = () => cleanup(false);
                this.closeBtn.onclick = () => cleanup(false);
            });
        },

        alert(title, message) {
            return this.show(title, message, 'alert');
        },

        confirm(title, message) {
            return this.show(title, message, 'confirm');
        }
    };

    // --- Utilities ---

    function updateThemeButtonText() {
        themeToggle.textContent = body.classList.contains('dark-theme') ? '☀️ Light Mode' : '🌙 Dark Mode';
    }

    // Theme Management
    const savedTheme = localStorage.getItem('theme') || 'dark-theme';
    body.className = savedTheme;
    updateThemeButtonText();

    themeToggle.addEventListener('click', () => {
        if (body.classList.contains('dark-theme')) {
            body.classList.replace('dark-theme', 'light-theme');
            localStorage.setItem('theme', 'light-theme');
        } else {
            body.classList.replace('light-theme', 'dark-theme');
            localStorage.setItem('theme', 'dark-theme');
        }
        updateThemeButtonText();
    });

    // Load session logic
    loadBtn.addEventListener('click', () => {
        lastMovedCommand = null; // Reset on new load
        fileInput.click();
    });

    fileInput.addEventListener('change', (e) => {
        const file = e.target.files[0];
        if (!file) return;

        const reader = new FileReader();
        reader.onload = (event) => {
            try {
                currentSession = JSON.parse(event.target.result);
                renderSession();
                saveBtn.disabled = false;
                playBtn.disabled = false;
            } catch (err) {
                modal.alert('Parsing Error', 'Error parsing JSON file. Please ensure it is a valid session recording.');
                console.error(err);
            }
        };
        reader.readAsText(file);
    });

    function renderSession() {
        if (!currentSession) return;

        // Render Metadata
        sessionName.value = currentSession.metadata.name || '';
        sessionModel.value = currentSession.metadata.model || '';
        sessionCreatedAt.value = currentSession.metadata.created_at || '';
        sessionDescription.value = currentSession.metadata.description || '';

        // Render Commands
        renderCommands();
    }

    function renderCommands() {
        const filter = commandFilter.value.toLowerCase();
        commandList.innerHTML = '';

        const filteredCommands = currentSession.commands.filter(cmd =>
            cmd.tool.toLowerCase().includes(filter)
        );

        commandCount.textContent = filteredCommands.length;

        if (filteredCommands.length === 0) {
            commandList.innerHTML = '<div class="empty-state">No commands found matching filter.</div>';
            return;
        }

        filteredCommands.forEach((cmd, index) => {
            const clone = commandTemplate.content.cloneNode(true);
            const card = clone.querySelector('.command-card');

            if (cmd === lastMovedCommand) {
                card.classList.add('moved-highlight');
                card.title = "Action: Moved";
            }

            card.querySelector('.index').textContent = `#${index + 1}`;
            card.querySelector('.tool-name').textContent = cmd.tool;

            const date = new Date(cmd.timestamp * 1000);
            card.querySelector('.timestamp').textContent = date.toLocaleTimeString();

            // Run command handler
            card.querySelector('.run-cmd').addEventListener('click', async (e) => {
                const btn = e.target;
                const originalText = btn.textContent;
                btn.disabled = true;
                btn.textContent = '...';
                card.style.borderColor = 'var(--accent-color)';

                const res = await runCommand(cmd.tool, cmd.arguments);

                btn.disabled = false;
                btn.textContent = originalText;

                if (res.error) {
                    card.style.borderColor = 'var(--danger-color)';
                    const errMsg = typeof res.error === 'string' ? res.error : JSON.stringify(res.error);
                    modal.alert('Execution Error', `Error: ${errMsg}`);
                } else {
                    card.style.borderColor = 'var(--success-color)';
                    card.classList.add('cmd-executed');
                    btn.disabled = true;
                    btn.textContent = '✓ Done';
                }
            });

            // Description editor
            const descTextarea = card.querySelector('.cmd-description');
            descTextarea.value = cmd.description || '';
            descTextarea.addEventListener('input', (e) => {
                cmd.description = e.target.value;
            });

            const editor = card.querySelector('#argsEditor');

            // Simple JSON textarea editor
            const textarea = document.createElement('textarea');
            textarea.value = JSON.stringify(cmd.arguments, null, 2);
            textarea.spellcheck = false;
            textarea.style.width = '100%';
            textarea.style.minHeight = '150px';
            textarea.style.fontFamily = '"JetBrains Mono", monospace';
            textarea.style.fontSize = '0.85rem';

            textarea.addEventListener('input', (e) => {
                try {
                    const newVal = JSON.parse(e.target.value);
                    cmd.arguments = newVal;
                    textarea.style.borderColor = 'var(--glass-border)';
                } catch (err) {
                    textarea.style.borderColor = 'var(--danger-color)';
                }
            });

            editor.appendChild(textarea);

            clone.querySelector('.delete-cmd').addEventListener('click', async () => {
                if (await modal.confirm('Confirm Deletion', 'Are you sure you want to delete this command?')) {
                    const originalIndex = currentSession.commands.indexOf(cmd);
                    currentSession.commands.splice(originalIndex, 1);
                    renderCommands();
                }
            });

            clone.querySelector('.move-up').addEventListener('click', () => {
                const originalIndex = currentSession.commands.indexOf(cmd);
                if (originalIndex > 0) {
                    lastMovedCommand = cmd;
                    const temp = currentSession.commands[originalIndex];
                    currentSession.commands[originalIndex] = currentSession.commands[originalIndex - 1];
                    currentSession.commands[originalIndex - 1] = temp;
                    renderCommands();
                }
            });

            clone.querySelector('.move-down').addEventListener('click', () => {
                const originalIndex = currentSession.commands.indexOf(cmd);
                if (originalIndex < currentSession.commands.length - 1) {
                    lastMovedCommand = cmd;
                    const temp = currentSession.commands[originalIndex];
                    currentSession.commands[originalIndex] = currentSession.commands[originalIndex + 1];
                    currentSession.commands[originalIndex + 1] = temp;
                    renderCommands();
                }
            });

            commandList.appendChild(clone);
        });
    }

    // Filter logic
    commandFilter.addEventListener('input', () => {
        renderCommands();
    });

    function sanitizeText(text) {
        if (!text) return '';
        // Remove non-ASCII characters (including emoticons like ✓, ✅, etc.)
        return text.replace(/[^\x00-\x7F]/g, '');
    }

    // Save logic
    saveBtn.addEventListener('click', () => {
        if (!currentSession) return;

        // Update metadata from inputs and sanitize
        currentSession.metadata.name = sanitizeText(sessionName.value);
        currentSession.metadata.model = sanitizeText(sessionModel.value);
        currentSession.metadata.description = sanitizeText(sessionDescription.value);

        // Sanitize all command descriptions
        currentSession.commands.forEach(cmd => {
            if (cmd.description) {
                cmd.description = sanitizeText(cmd.description);
            }
        });

        const blob = new Blob([JSON.stringify(currentSession, null, 2)], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `${currentSession.metadata.name.replace(/\s+/g, '_')}_edited.json`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    });
});

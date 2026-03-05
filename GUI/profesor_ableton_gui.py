# Profesor Abelton GUI
# Text and Voice Interface for Ableton Live
# Version: 2.0.0

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, simpledialog
import socket
import json
import threading
import time
import os
import sys
import platform

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

try:
    from Utils.api_key_manager import APIKeyManager
except Exception:
    APIKeyManager = None

try:
    import speech_recognition as sr
except ImportError:
    sr = None
    print("⚠️ Voice recognition not available. Install: pip install SpeechRecognition")

try:
    from pystray import Icon, Menu, MenuItem
    from PIL import Image, ImageDraw
    TRAY_AVAILABLE = True
except ImportError:
    TRAY_AVAILABLE = False
    print("⚠️ System tray not available. Install: pip install pystray pillow")


class ProfesorAbeltonGUI:
    """Main GUI application for Profesor Abelton"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("🎓 Profesor Abelton")
        self.root.geometry("420x900")
        self.root.minsize(350, 600)
        
        # Configuration
        self.config = self.load_config()
        self.server_host = self.config.get("server", {}).get("host", "localhost")
        self.server_port = self.config.get("server", {}).get("port", 8766)
        
        # API Keys (encrypted on disk, per-machine)
        self.api_key_manager = APIKeyManager() if APIKeyManager else None
        self.api_keys = self.api_key_manager.load_keys() if self.api_key_manager else {}

        # One-time migration: move any plaintext keys from config into encrypted storage, then sanitize config.
        plaintext_keys = self.config.get("api_keys", {})
        if self.api_key_manager and isinstance(plaintext_keys, dict) and plaintext_keys:
            merged = dict(plaintext_keys)
            merged.update(self.api_keys)  # encrypted storage wins if both exist
            self.api_keys = merged
            try:
                self.api_key_manager.save_keys(self.api_keys)
            except Exception:
                self.api_keys = self.api_key_manager.load_keys()
            self.config.pop("api_keys", None)
            self.save_config()
        else:
            self.config.pop("api_keys", None)

        # Provider selection
        self.provider_var = tk.StringVar(value=self.config.get("ai_providers", {}).get("default", "GROQ"))

        # Voice recognition
        self.recognizer = sr.Recognizer() if sr else None
        self.microphone = sr.Microphone() if sr else None
        self.is_listening = False
        self.current_language = "en"  # 'en' or 'hr'
        
        # Current state
        self.ableton_state = {}
        self.chat_history = []
        
        # System tray
        self.tray_icon = None
        self.is_hidden = False
        
        # Setup UI
        self.setup_ui()

        # Ensure the window shows in the Windows taskbar (not only Alt+Tab).
        self._ensure_taskbar_icon()

        # Window protocol (minimize to tray)
        if TRAY_AVAILABLE:
            self.root.protocol('WM_DELETE_WINDOW', self.hide_to_tray)
        
        # Start state monitor
        self.monitor_thread = threading.Thread(target=self.monitor_connection, daemon=True)
        self.monitor_thread.start()
    
    def _ensure_taskbar_icon(self):
        """
        Windows-only: force app window style so the GUI is visible in the taskbar.
        This fixes the common issue: window is reachable via Alt+Tab but has no taskbar button.
        """
        if platform.system() != "Windows":
            return

        try:
            import ctypes  # Windows only
            try:
                # Helps Windows group the taskbar button under our app, not under the parent console host.
                ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("ProfesorAbelton")  # type: ignore[attr-defined]
            except Exception:
                pass

            GWL_EXSTYLE = -20
            GWLP_HWNDPARENT = -8
            WS_EX_APPWINDOW = 0x00040000
            WS_EX_TOOLWINDOW = 0x00000080
            SWP_NOSIZE = 0x0001
            SWP_NOMOVE = 0x0002
            SWP_NOZORDER = 0x0004
            SWP_FRAMECHANGED = 0x0020
            GA_ROOT = 2
            SW_RESTORE = 9

            def _apply():
                try:
                    # Apply only once per process to avoid Tk/Win32 weirdness (ghost/duplicate windows).
                    if getattr(self, "_taskbar_fix_applied", False):
                        return

                    self.root.update_idletasks()
                    hwnd_child = self.root.winfo_id()
                    if not hwnd_child:
                        return

                    user32 = ctypes.windll.user32

                    # On Windows, Tk uses a wrapper HWND (top-level) plus an inner child HWND.
                    # Tkinter's winfo_id() frequently returns the *child* window handle.
                    # Taskbar/owner/exstyle must be applied to the *wrapper* HWND, otherwise you can
                    # end up with a second white window and/or missing caption buttons.
                    hwnd = user32.GetAncestor(hwnd_child, GA_ROOT) or hwnd_child

                    # Owned windows don't appear in the taskbar. Ensure no owner/parent is set.
                    try:
                        set_long_ptr = getattr(user32, "SetWindowLongPtrW", None)
                        if set_long_ptr is None:
                            set_long_ptr = user32.SetWindowLongW  # type: ignore[attr-defined]
                        set_long_ptr(hwnd, GWLP_HWNDPARENT, 0)
                    except Exception:
                        pass

                    # Use Get/SetWindowLongPtr when available (64-bit safe).
                    get_long_ptr = getattr(user32, "GetWindowLongPtrW", None)
                    if get_long_ptr is None:
                        get_long_ptr = user32.GetWindowLongW  # type: ignore[attr-defined]

                    set_long_ptr_ex = getattr(user32, "SetWindowLongPtrW", None)
                    if set_long_ptr_ex is None:
                        set_long_ptr_ex = user32.SetWindowLongW  # type: ignore[attr-defined]

                    style = get_long_ptr(hwnd, GWL_EXSTYLE)
                    style = style & ~WS_EX_TOOLWINDOW
                    style = style | WS_EX_APPWINDOW
                    set_long_ptr_ex(hwnd, GWL_EXSTYLE, style)

                    # Refresh window frame
                    try:
                        user32.SetWindowPos(
                            hwnd,
                            0,
                            0,
                            0,
                            0,
                            0,
                            SWP_NOMOVE | SWP_NOSIZE | SWP_NOZORDER | SWP_FRAMECHANGED,
                        )
                    except Exception:
                        pass

                    # Nudge Windows shell to re-evaluate taskbar visibility for this window.
                    # Without this, style changes sometimes only affect Alt+Tab but not the taskbar button.
                    try:
                        user32.ShowWindow(hwnd, SW_RESTORE)
                    except Exception:
                        pass

                    try:
                        if getattr(self, "_taskbar_shell_kick_done", False) is False:
                            self._taskbar_shell_kick_done = True
                            # Do NOT change "minimize to tray" behavior: this only runs once at startup.
                            self.root.after(
                                10,
                                lambda: (
                                    self.root.withdraw(),
                                    self.root.after(30, self.root.deiconify),
                                ),
                            )
                    except Exception:
                        pass

                    self._taskbar_fix_applied = True
                except Exception:
                    pass

            try:
                self.root.bind("<Map>", lambda _e: _apply())
            except Exception:
                pass
            self.root.after(250, _apply)
        except Exception:
            return

    def load_config(self):
        """Load configuration"""
        config_path = os.path.join(os.path.dirname(__file__), "..", "Config", "copilot_config.json")
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {
                "server": {"host": "localhost", "port": 8766},
                "api_keys": {}
            }
    
    def update_mcp_status(self):
        """Update MCP status indicator (always ON now)"""
        # MCP is now always enabled
        self.mcp_status_label.config(text="[MCP: ON]", fg='#00ff88')

    def save_config(self):
        """Save configuration"""
        config_path = os.path.join(os.path.dirname(__file__), "..", "Config", "copilot_config.json")
        try:
            # Never store API keys in plaintext config.
            self.config.pop("api_keys", None)
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save config: {e}")
    
    def setup_ui(self):
        """Setup modern Gumroad-friendly interface"""
        # Modern Gumroad-ready color scheme
        BG_DARK = '#0a0a0a'        # Deep black background
        BG_HEADER = '#1a1a1a'      # Dark header
        BG_PANEL = '#2a2a2a'       # Panel background
        BG_ACCENT = '#3a3a3a'      # Accent panels
        FG_TEXT = '#e0e0e0'        # Light text
        FG_DIM = '#888888'         # Dimmed text
        ACCENT_BLUE = '#00d4ff'    # Bright cyan accent
        ACCENT_GREEN = '#00ff88'   # Bright green for success
        ACCENT_ORANGE = '#ff6b35'  # Warm orange for warnings
        BORDER_COLOR = '#404040'   # Subtle borders

        # Configure root background and styling
        self.root.configure(bg=BG_DARK)
        self.style = {'bg': BG_DARK, 'fg': FG_TEXT, 'font': ('Segoe UI', 10)}

        # ============= MODERN HEADER SECTION =============
        # Avoid fixed-height headers: they can clip text on Windows DPI scaling (125%/150%).
        header_frame = tk.Frame(self.root, bg=BG_HEADER)
        header_frame.pack(side=tk.TOP, fill=tk.X, padx=0, pady=0)

        # Main branding section
        branding_frame = tk.Frame(header_frame, bg=BG_HEADER)
        branding_frame.pack(fill=tk.X, padx=20, pady=(15, 10))

        # Logo and title
        logo_frame = tk.Frame(branding_frame, bg=BG_HEADER)
        logo_frame.pack(side=tk.LEFT)

        # Modern logo design (ASCII instead of emoji)
        logo_label = tk.Label(
            logo_frame,
            text="[AI]",
            font=('Segoe UI', 14, 'bold'),
            bg=BG_ACCENT,
            fg=ACCENT_BLUE,
            padx=6,
            pady=2,
            relief=tk.RAISED,
            bd=1
        )
        logo_label.pack(side=tk.LEFT, padx=(0, 8))

        title_frame = tk.Frame(logo_frame, bg=BG_HEADER)
        title_frame.pack(side=tk.LEFT)

        title_main = tk.Label(
            title_frame,
            text="PROFESOR",
            font=('Segoe UI', 16, 'bold'),
            bg=BG_HEADER,
            fg='white'
        )
        title_main.pack(anchor=tk.W)

        title_sub = tk.Label(
            title_frame,
            text="ABELTON",
            font=('Segoe UI', 12, 'bold'),
            bg=BG_HEADER,
            fg=ACCENT_BLUE
        )
        title_sub.pack(anchor=tk.W)

        # Version badge
        version_label = tk.Label(
            branding_frame,
            text="v2.0.0",
            font=('Segoe UI', 8),
            bg=BG_ACCENT,
            fg=FG_TEXT,
            padx=8,
            pady=2,
            relief=tk.FLAT
        )
        version_label.pack(side=tk.RIGHT, padx=(10, 0))

        # Status indicators panel
        status_panel = tk.Frame(header_frame, bg=BG_PANEL, relief=tk.RIDGE, bd=1)
        status_panel.pack(fill=tk.X, padx=20, pady=(0, 15))

        # Status grid
        status_title = tk.Label(
            status_panel,
            text="SYSTEM STATUS",
            font=('Segoe UI', 9, 'bold'),
            bg=BG_PANEL,
            fg=FG_DIM
        )
        status_title.pack(pady=(8, 5))

        status_grid = tk.Frame(status_panel, bg=BG_PANEL)
        status_grid.pack(pady=(0, 8))

        # Server status
        server_frame = tk.Frame(status_grid, bg=BG_PANEL)
        server_frame.pack(side=tk.LEFT, padx=15)

        self.server_status_icon = tk.Label(
            server_frame,
            text="[X]",
            font=('Segoe UI', 10, 'bold'),
            bg=BG_PANEL,
            fg=ACCENT_ORANGE
        )
        self.server_status_icon.pack(side=tk.LEFT, padx=(0, 5))

        self.server_status_label = tk.Label(
            server_frame,
            text="Server",
            font=('Segoe UI', 9),
            bg=BG_PANEL,
            fg=FG_TEXT
        )
        self.server_status_label.pack(side=tk.LEFT)

        # Ableton status
        ableton_frame = tk.Frame(status_grid, bg=BG_PANEL)
        ableton_frame.pack(side=tk.LEFT, padx=15)

        self.ableton_status_icon = tk.Label(
            ableton_frame,
            text="[X]",
            font=('Segoe UI', 10, 'bold'),
            bg=BG_PANEL,
            fg=ACCENT_ORANGE
        )
        self.ableton_status_icon.pack(side=tk.LEFT, padx=(0, 5))

        self.ableton_status_label = tk.Label(
            ableton_frame,
            text="Ableton",
            font=('Segoe UI', 9),
            bg=BG_PANEL,
            fg=FG_TEXT
        )
        self.ableton_status_label.pack(side=tk.LEFT)

        # MCP status moved to status bar
        
        # ============= MODERN CHAT SECTION =============
        chat_panel = tk.Frame(self.root, bg=BG_ACCENT, relief=tk.RIDGE, bd=1)
        chat_panel.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=15, pady=(5, 10))

        # Chat header
        # Avoid fixed-height headers: they can clip text on Windows DPI scaling (125%/150%).
        chat_header = tk.Frame(chat_panel, bg=BG_ACCENT)
        chat_header.pack(fill=tk.X, padx=15, pady=(10, 5))

        chat_title = tk.Label(
            chat_header,
            text="🤖 AI CONVERSATION",
            font=('Segoe UI', 10, 'bold'),
            bg=BG_ACCENT,
            fg=ACCENT_BLUE
        )
        chat_title.pack(side=tk.LEFT)

        # Clear chat button
        clear_btn = tk.Button(
            chat_header,
            text="🗑️",
            font=('Segoe UI', 9),
            bg=BG_ACCENT,
            fg=FG_TEXT,
            relief=tk.FLAT,
            cursor='hand2',
            command=self.clear_chat,
            padx=8,
            pady=2
        )
        clear_btn.pack(side=tk.RIGHT)

        # Chat display area
        chat_container = tk.Frame(chat_panel, bg=BG_DARK, relief=tk.SUNKEN, bd=1)
        chat_container.pack(fill=tk.BOTH, expand=True, padx=15, pady=(0, 15))

        self.chat_display = scrolledtext.ScrolledText(
            chat_container,
            wrap=tk.WORD,
            font=('Segoe UI', 10),
            bg=BG_DARK,
            fg=FG_TEXT,
            insertbackground=ACCENT_BLUE,
            relief=tk.FLAT,
            padx=12,
            pady=12,
            selectbackground=BG_ACCENT,
            selectforeground='white'
        )
        self.chat_display.pack(fill=tk.BOTH, expand=True)

        # Configure modern tags for colored messages
        self.chat_display.tag_config('user', foreground=ACCENT_GREEN, font=('Segoe UI', 10, 'bold'))
        self.chat_display.tag_config('ai', foreground=FG_TEXT, font=('Segoe UI', 10))
        self.chat_display.tag_config('system', foreground=ACCENT_BLUE, font=('Segoe UI', 9, 'italic'))
        self.chat_display.tag_config('error', foreground=ACCENT_ORANGE, font=('Segoe UI', 10, 'bold'))
        self.chat_display.tag_config('timestamp', foreground=FG_DIM, font=('Segoe UI', 8))
        
        # Controls are now integrated in the modern input panel below
        
        # ============= MODERN INPUT SECTION =============
        # Avoid fixed-height input panel: allow it to size to its contents.
        input_panel = tk.Frame(self.root, bg=BG_ACCENT, relief=tk.RIDGE, bd=1)
        input_panel.pack(side=tk.BOTTOM, fill=tk.X, padx=15, pady=(0, 15))

        # Input header
        # Avoid fixed-height header row: buttons/text can get clipped on DPI scaling.
        input_header = tk.Frame(input_panel, bg=BG_ACCENT)
        input_header.pack(fill=tk.X, padx=15, pady=(8, 5))

        # Compact provider selector
        provider_combo = ttk.Combobox(
            input_header,
            textvariable=self.provider_var,
            values=["GROQ", "CLAUDE"],
            width=7,
            state='readonly',
            font=('Segoe UI', 7)
        )
        provider_combo.pack(side=tk.LEFT, padx=(0, 10))

        input_title = tk.Label(
            input_header,
            text="💬 YOUR MESSAGE",
            font=('Segoe UI', 9, 'bold'),
            bg=BG_ACCENT,
            fg=ACCENT_BLUE
        )
        input_title.pack(side=tk.LEFT)

        # Control buttons
        controls_frame = tk.Frame(input_header, bg=BG_ACCENT)
        controls_frame.pack(side=tk.RIGHT)

        # Voice button (modern design)
        voice_state = 'normal' if sr else 'disabled'
        voice_bg = ACCENT_BLUE if sr else BG_ACCENT
        self.voice_button = tk.Button(
            controls_frame,
            text="VOICE",
            font=('Segoe UI', 8, 'bold'),
            bg=voice_bg,
            fg='white' if sr else FG_DIM,
            relief=tk.FLAT,
            cursor='hand2' if sr else 'arrow',
            state=voice_state,
            command=self.toggle_voice,
            padx=12,
            pady=4,
            borderwidth=0
        )
        self.voice_button.pack(side=tk.LEFT, padx=(0, 5))

        # Send button (primary action)
        self.send_button = tk.Button(
            controls_frame,
            text="SEND",
            font=('Segoe UI', 8, 'bold'),
            bg=ACCENT_GREEN,
            fg='white',
            relief=tk.FLAT,
            cursor='hand2',
            command=self.send_message,
            padx=12,
            pady=4,
            borderwidth=0
        )
        self.send_button.pack(side=tk.LEFT, padx=(0, 5))

        # Settings button
        settings_btn = tk.Button(
            controls_frame,
            text="SETTINGS",
            font=('Segoe UI', 7, 'bold'),
            bg=BG_ACCENT,
            fg=FG_TEXT,
            relief=tk.FLAT,
            cursor='hand2',
            command=self.show_settings,
            padx=8,
            pady=4
        )
        settings_btn.pack(side=tk.LEFT, padx=(0, 5))

        # System tray button
        if TRAY_AVAILABLE:
            tray_btn = tk.Button(
                controls_frame,
                text="HIDE",
                font=('Segoe UI', 7, 'bold'),
                bg=BG_ACCENT,
                fg=FG_TEXT,
                relief=tk.FLAT,
                cursor='hand2',
                command=self.hide_to_tray,
                padx=8,
                pady=4
            )
            tray_btn.pack(side=tk.LEFT)
        
        # Modern text input area
        input_area = tk.Frame(input_panel, bg=BG_DARK, relief=tk.SUNKEN, bd=1)
        input_area.pack(fill=tk.BOTH, expand=True, padx=15, pady=(0, 15))

        self.input_field = tk.Text(
            input_area,
            height=3,
            font=('Segoe UI', 10),
            bg=BG_DARK,
            fg=FG_TEXT,
            insertbackground=ACCENT_BLUE,
            relief=tk.FLAT,
            padx=12,
            pady=12,
            wrap=tk.WORD,
            selectbackground=BG_ACCENT,
            selectforeground='white'
        )
        self.input_field.pack(fill=tk.BOTH, expand=True)
        self.input_field.bind('<Return>', self.on_enter_key)
        self.input_field.bind('<Shift-Return>', lambda e: None)  # Allow Shift+Enter for newline

        # Placeholder text
        self.input_field.insert('1.0', 'Type your message to Profesor Ableton...')
        self.input_field.config(fg=FG_DIM)

        def on_focus_in(event):
            if self.input_field.get('1.0', 'end-1c') == 'Type your message to Profesor Ableton...':
                self.input_field.delete('1.0', tk.END)
                self.input_field.config(fg=FG_TEXT)

        def on_focus_out(event):
            if not self.input_field.get('1.0', 'end-1c').strip():
                self.input_field.insert('1.0', 'Type your message to Profesor Ableton...')
                self.input_field.config(fg=FG_DIM)

        self.input_field.bind('<FocusIn>', on_focus_in)
        self.input_field.bind('<FocusOut>', on_focus_out)

        # Status bar at bottom
        # Avoid fixed-height status bar: can clip descenders on some fonts/scales.
        status_bar = tk.Frame(self.root, bg=BG_HEADER, relief=tk.RIDGE, bd=1)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X, padx=0, pady=0)

        # Status info (no emoji)
        status_info = tk.Label(
            status_bar,
            text="Ready to produce music with AI assistance",
            font=('Segoe UI', 8),
            bg=BG_HEADER,
            fg=FG_DIM
        )
        status_info.pack(side=tk.LEFT, padx=15)

        # MCP status in status bar
        self.mcp_status_label = tk.Label(
            status_bar,
            text="🔧 MCP: OFF",
            font=('Segoe UI', 8),
            bg=BG_HEADER,
            fg=FG_DIM
        )
        self.mcp_status_label.pack(side=tk.LEFT, padx=(10, 0))

        # Update MCP status (force ON since we hardcoded it)
        self.update_mcp_status()

        # Version info
        version_info = tk.Label(
            status_bar,
            text="Profesor Ableton v2.0.0",
            font=('Segoe UI', 8),
            bg=BG_HEADER,
            fg=FG_DIM
        )
        version_info.pack(side=tk.RIGHT, padx=15)
        
        # Welcome message (no emoji)
        self.add_system_message("Profesor Abelton ready!")
        self.add_system_message("Connect to server and Ableton to start...")
    
    def on_enter_key(self, event):
        """Handle Enter key - send message, Shift+Enter for newline"""
        if event.state & 0x1:  # Shift is pressed
            return  # Allow newline
        else:
            self.send_message()
            return 'break'  # Prevent newline
    
    def add_message(self, text, tag='system'):
        """Add message to chat display"""
        self.chat_display.insert(tk.END, text + '\n\n', tag)
        self.chat_display.see(tk.END)
    
    def add_user_message(self, text):
        """Add user message"""
        self.add_message(f"👤 You: {text}", 'user')
    
    def add_ai_message(self, text, provider='AI'):
        """Add AI message"""
        self.add_message(f"🎓 Profesor ({provider}): {text}", 'ai')
    
    def add_system_message(self, text):
        """Add system message"""
        self.add_message(f"💡 {text}", 'system')
    
    def add_error_message(self, text):
        """Add error message"""
        self.add_message(f"❌ Error: {text}", 'error')
    
    def send_message(self):
        """Send text message to AI"""
        message = self.input_field.get("1.0", tk.END).strip()
        
        if not message:
            return
        
        self.input_field.delete("1.0", tk.END)
        self.add_user_message(message)
        
        # Send to server in background
        threading.Thread(
            target=self.send_to_server,
            args=('command', message),
            daemon=True
        ).start()
    
    def send_to_server(self, msg_type, content):
        """Send message to server"""
        sock = None
        try:
            # Create socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(10.0)
            
            print(f"🔌 Connecting to {self.server_host}:{self.server_port}...")
            sock.connect((self.server_host, self.server_port))
            print(f"✅ Connected")

            # IMPORTANT: First, register as GUI client
            connect_msg = {
                "type": "connect",
                "client": "gui"
            }
            print(f"📤 Sending connect message...")
            sock.sendall(json.dumps(connect_msg).encode('utf-8') + b'\n')
            
            # Wait for connect response
            print(f"📥 Waiting for connect response...")
            connect_response = sock.recv(8192).decode('utf-8')
            print(f"📨 Received: {connect_response[:100]}")
            
            if '\n' in connect_response:
                connect_response = connect_response.split('\n')[0]
            
            if connect_response.strip():
                connect_result = json.loads(connect_response.strip())
                
                if connect_result.get("status") != "ok":
                    raise Exception(f"Server rejected connection: {connect_result}")
                print(f"✅ Connection accepted")
            
            # Get API key for provider
            provider = self.provider_var.get()
            api_key = self.api_keys.get(provider, "")

            # Update environment variable for Claude MCP
            if provider == "CLAUDE":
                os.environ["CLAUDE_MCP_ENABLED"] = "true"
                os.environ["CLAUDE_API_KEY"] = api_key if api_key else ""

            # Prepare command message
            message = {
                "type": msg_type,
                "prompt": content,
                "language": self.current_language,
                "provider": provider,
                "api_key": api_key if api_key else None
            }

            # Send command with newline delimiter
            print(f"📤 Sending command...")
            sock.settimeout(60.0)  # Longer timeout for AI response
            sock.sendall(json.dumps(message).encode('utf-8') + b'\n')

            # Receive response
            print(f"📥 Waiting for AI response...")
            response_data = sock.recv(16384).decode('utf-8')
            print(f"📨 Received response: {len(response_data)} bytes")
            
            if '\n' in response_data:
                response_data = response_data.split('\n')[0]
            
            if not response_data.strip():
                raise Exception("Empty response from server")
                
            response = json.loads(response_data.strip())

            # Handle response
            if 'error' in response:
                self.add_error_message(response['error'])
            elif 'response' in response:
                provider_name = response.get('provider', 'AI')
                self.add_ai_message(response['response'], provider_name)

                # Show tool calls if MCP was used
                if 'tool_calls' in response and response['tool_calls']:
                    self.add_system_message(f"MCP Tools used: {len(response['tool_calls'])}")

                # Execute commands if any
                if 'commands' in response and response['commands']:
                    self.add_system_message(f"Executing {len(response['commands'])} command(s)...")
            else:
                self.add_system_message("Response received")

        except socket.timeout:
            self.add_error_message("Server timeout. Make sure server is running!")
        except ConnectionRefusedError:
            self.add_error_message("Cannot connect to server. Make sure it's running!")
        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()
            self.add_error_message(f"Communication error: {e}")
        finally:
            if sock:
                try:
                    sock.close()
                    print(f"🔌 Socket closed")
                except:
                    pass
    
    def toggle_voice(self):
        """Toggle voice listening"""
        if not sr or not self.recognizer or not self.microphone:
            messagebox.showerror("Voice Not Available", 
                                 "Voice recognition not installed.\nInstall: pip install SpeechRecognition pyaudio")
            return
        
        if self.is_listening:
            self.is_listening = False
            self.voice_button.config(text="🎤 Voice", bg='#007acc')
            self.add_system_message("Voice recognition stopped")
        else:
            self.is_listening = True
            self.voice_button.config(text="⏹️ Stop", bg='#d13438')
            lang = "EN" if self.current_language == "en" else "HR"
            self.add_system_message(f"🎤 Listening ({lang})... Speak now!")
            
            # Start listening in background
            threading.Thread(target=self.listen_voice, daemon=True).start()
    
    def listen_voice(self):
        """Listen for voice input"""
        try:
            with self.microphone as source:
                # Adjust for ambient noise
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                
                # Listen
                audio = self.recognizer.listen(source, timeout=10, phrase_time_limit=15)
            
            # Recognize
            lang_code = "en-US" if self.current_language == "en" else "hr-HR"
            text = self.recognizer.recognize_google(audio, language=lang_code)
            
            self.add_user_message(f"🎤 {text}")
            
            # Send to server
            threading.Thread(
                target=self.send_to_server,
                args=('command', text),
                daemon=True
            ).start()
            
        except sr.WaitTimeoutError:
            self.add_error_message("Timeout - no speech detected")
        except sr.UnknownValueError:
            self.add_error_message("Could not understand audio")
        except sr.RequestError as e:
            self.add_error_message(f"Recognition service error: {e}")
        except Exception as e:
            self.add_error_message(f"Voice error: {e}")
        finally:
            self.is_listening = False
            self.voice_button.config(text="🎤 Voice", bg='#007acc')
    
    def change_language(self, event):
        """Change voice language"""
        lang = self.language_var.get()
        self.current_language = "en" if lang == "English" else "hr"
        self.add_system_message(f"Language changed to: {lang}")
    
    def clear_chat(self):
        """Clear chat display"""
        self.chat_display.delete(1.0, tk.END)
        self.add_system_message("Chat cleared")
    
    def show_help(self):
        """Show help dialog"""
        help_text = """
🎓 Profesor Abelton - Help

TEXT COMMANDS:
• Type any question or instruction
• Examples:
  - "Create a new MIDI track"
  - "Set tempo to 128 BPM"
  - "Explain what a compressor does"
  - "Add reverb to track 1"

VOICE COMMANDS:
• Click "Voice" button to start
• Speak clearly
• Supports English and Croatian

LANGUAGE:
• English: General commands and production
• Croatian: Full Croatian language support

AI PROVIDERS:
• GROQ: Groq Cloud (requires API key)
• CLAUDE: Anthropic Claude (requires API key)

SETTINGS:
• Click ⚙️ to enter API keys
• Set API keys for Groq and Claude

MINIMIZE:
• Click ⬇️ to minimize to system tray
• Right-click icon for menu

For more info, see README.md
        """
        
        help_window = tk.Toplevel(self.root)
        help_window.title("Help")
        help_window.geometry("500x600")
        help_window.configure(bg='#1e1e1e')
        
        help_text_widget = scrolledtext.ScrolledText(
            help_window,
            wrap=tk.WORD,
            font=('Segoe UI', 10),
            bg='#1e1e1e',
            fg='#cccccc',
            padx=15,
            pady=15
        )
        help_text_widget.pack(fill=tk.BOTH, expand=True)
        help_text_widget.insert(1.0, help_text)
        help_text_widget.config(state=tk.DISABLED)
    
    def show_settings(self):
        """Show settings dialog for API keys"""
        # Prevent multiple settings windows
        if hasattr(self, 'settings_window') and self.settings_window and self.settings_window.winfo_exists():
            self.settings_window.lift()  # Bring to front
            return

        settings_window = tk.Toplevel(self.root)
        self.settings_window = settings_window  # Store reference
        settings_window.title("⚙️ Settings - API Keys")
        settings_window.geometry("500x450")
        settings_window.configure(bg='#2d2d30')
        settings_window.resizable(False, False)
        
        # Title
        title_label = tk.Label(
            settings_window,
            text="🔑 API Keys",
            font=('Segoe UI', 14, 'bold'),
            bg='#2d2d30',
            fg='white'
        )
        title_label.pack(pady=15)
        
        # Info
        info_label = tk.Label(
            settings_window,
            text="Enter API keys for AI providers.",
            font=('Segoe UI', 9),
            bg='#2d2d30',
            fg='#cccccc',
            justify=tk.LEFT
        )
        info_label.pack(pady=(0, 15))
        
        # Frame for inputs
        inputs_frame = tk.Frame(settings_window, bg='#2d2d30')
        inputs_frame.pack(padx=30, pady=10, fill=tk.BOTH, expand=True)
        
        # API key entries
        providers = ["GROQ", "CLAUDE"]
        entries = {}
        
        for i, provider in enumerate(providers):
            # Label
            label = tk.Label(
                inputs_frame,
                text=f"{provider}:",
                font=('Segoe UI', 10, 'bold'),
                bg='#2d2d30',
                fg='white',
                width=10,
                anchor='w'
            )
            label.grid(row=i, column=0, sticky=tk.W, pady=8)
            
            # Entry
            entry = tk.Entry(
                inputs_frame,
                font=('Segoe UI', 9),
                bg='#3c3c3c',
                fg='white',
                insertbackground='white',
                show='•',
                width=40
            )
            entry.grid(row=i, column=1, sticky=(tk.W, tk.E), pady=8, padx=10)
            entry.insert(0, self.api_keys.get(provider, ""))
            entries[provider] = entry
        
        inputs_frame.columnconfigure(1, weight=1)

        # MCP Status (Always Enabled)
        mcp_frame = tk.Frame(settings_window, bg='#2d2d30', relief=tk.RIDGE, bd=2)
        mcp_frame.pack(padx=30, pady=(10, 20), fill=tk.X)

        mcp_title = tk.Label(
            mcp_frame,
            text="🤖 MCP Status: ALWAYS ENABLED",
            font=('Segoe UI', 12, 'bold'),
            bg='#2d2d30',
            fg='#00ff88'
        )
        mcp_title.pack(pady=(10, 5))

        mcp_info = tk.Label(
            mcp_frame,
            text="MCP (Model Context Protocol) is always enabled.\nClaude can directly control Ableton functions!",
            font=('Segoe UI', 9),
            bg='#2d2d30',
            fg='#cccccc',
            justify=tk.LEFT
        )
        mcp_info.pack(pady=(0, 10))

        # Force MCP ON
        os.environ["CLAUDE_MCP_ENABLED"] = "true"
        self.config["mcp_enabled"] = True

        # Buttons
        button_frame = tk.Frame(settings_window, bg='#2d2d30')
        button_frame.pack(pady=20)
        
        def save_keys():
            if not self.api_key_manager:
                messagebox.showerror(
                    "Missing Dependency",
                    "Secure API key storage is not available.\n\nInstall with:\n  pip install cryptography"
                )
                return

            # Save API keys
            for provider, entry in entries.items():
                key = entry.get().strip()
                if key:
                    self.api_keys[provider] = key
                elif provider in self.api_keys:
                    del self.api_keys[provider]

            # Persist encrypted keys
            try:
                self.api_key_manager.save_keys(self.api_keys)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to securely save API keys: {e}")
                return

            # Save MCP setting
            os.environ["CLAUDE_MCP_ENABLED"] = "true"  # Always ON
            self.config["mcp_enabled"] = True  # Save to config
            self.save_config()
            self.add_system_message("✅ Settings saved! MCP: ON")
            self.update_mcp_status()
            settings_window.destroy()
            self.settings_window = None  # Clear reference
        
        def cancel():
            settings_window.destroy()
        
        save_btn = tk.Button(
            button_frame,
            text="💾 Save",
            font=('Segoe UI', 10, 'bold'),
            bg='#007acc',
            fg='white',
            relief=tk.FLAT,
            cursor='hand2',
            command=save_keys,
            padx=20,
            pady=10
        )
        save_btn.pack(side=tk.LEFT, padx=5)
        
        cancel_btn = tk.Button(
            button_frame,
            text="✖️ Cancel",
            font=('Segoe UI', 10),
            bg='#555',
            fg='white',
            relief=tk.FLAT,
            cursor='hand2',
            command=cancel,
            padx=20,
            pady=10
        )
        cancel_btn.pack(side=tk.LEFT, padx=5)
    
    def hide_to_tray(self):
        """Hide window to system tray"""
        if not TRAY_AVAILABLE:
            self.root.iconify()  # Fallback to minimize
            return
        
        self.root.withdraw()
        self.is_hidden = True
        
        if not self.tray_icon:
            # Create tray icon
            def create_image():
                # Create a simple icon
                width = 64
                height = 64
                image = Image.new('RGB', (width, height), (0, 122, 204))
                dc = ImageDraw.Draw(image)
                dc.text((10, 20), "PA", fill='white')
                return image
            
            def on_clicked(icon, item):
                self.show_from_tray()
            
            def on_quit(icon, item):
                icon.stop()
                self.root.quit()
            
            menu = Menu(
                MenuItem('Open', on_clicked, default=True),
                MenuItem('Exit', on_quit)
            )
            
            self.tray_icon = Icon("Profesor Abelton", create_image(), "Profesor Abelton", menu)
            
            # Run tray icon in background
            threading.Thread(target=self.tray_icon.run, daemon=True).start()
    
    def show_from_tray(self):
        """Show window from system tray"""
        self.root.deiconify()
        self.root.lift()
        self.root.focus_force()
        self.is_hidden = False
    
    def monitor_connection(self):
        """Monitor server and Ableton connection"""
        retry_count = 0
        max_retries_before_pause = 3
        
        while True:
            try:
                # Try to connect
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(3.0)
                sock.connect((self.server_host, self.server_port))

                # Send ping
                ping_msg = {"type": "ping"}
                sock.sendall(json.dumps(ping_msg).encode('utf-8') + b'\n')

                # Receive response with timeout
                sock.settimeout(5.0)  # Longer timeout for recv
                response_data = sock.recv(2048).decode('utf-8')
                
                # Handle multiple messages (take first one)
                if '\n' in response_data:
                    response_str = response_data.split('\n')[0]
                else:
                    response_str = response_data
                    
                response_str = response_str.strip()
                
                if response_str:
                    response = json.loads(response_str)
                    
                    sock.close()

                    # Update GUI from main thread
                    def update_gui():
                        # Update server status
                        self.server_status_icon.config(text="[OK]", fg="#00ff88")
                        self.server_status_label.config(text="Server OK")

                        # Update Ableton status
                        if response.get("ableton_connected", False):
                            self.ableton_status_icon.config(text="[OK]", fg="#00ff88")
                            self.ableton_status_label.config(text="Ableton OK")
                        else:
                            self.ableton_status_icon.config(text="[?]", fg="#ff6b35")
                            self.ableton_status_label.config(text="Waiting...")

                    self.root.after(0, update_gui)
                    retry_count = 0  # Reset retry count on success
                else:
                    sock.close()
                    raise Exception("Empty response from server")

            except socket.timeout:
                retry_count += 1
                print(f"⚠️ Monitor timeout (attempt {retry_count})")
                def update_error():
                    self.server_status_icon.config(text="[X]", fg="#ff6b35")
                    self.server_status_label.config(text="Timeout")
                    self.ableton_status_icon.config(text="[?]", fg="#888888")
                    self.ableton_status_label.config(text="Waiting...")
                self.root.after(0, update_error)
                
            except ConnectionRefusedError:
                retry_count += 1
                print(f"⚠️ Server not running (attempt {retry_count})")
                def update_error():
                    self.server_status_icon.config(text="[X]", fg="#ff6b35")
                    self.server_status_label.config(text="Not Running")
                    self.ableton_status_icon.config(text="[?]", fg="#888888")
                    self.ableton_status_label.config(text="N/A")
                self.root.after(0, update_error)
                
            except Exception as e:
                retry_count += 1
                print(f"⚠️ Monitor error: {e} (attempt {retry_count})")
                def update_error():
                    self.server_status_icon.config(text="[X]", fg="#ff6b35")
                    self.server_status_label.config(text="Error")
                    self.ableton_status_icon.config(text="[?]", fg="#888888")
                    self.ableton_status_label.config(text="N/A")
                self.root.after(0, update_error)

            # Adaptive sleep - sleep longer if multiple failures
            if retry_count >= max_retries_before_pause:
                time.sleep(10)  # Longer pause after multiple failures
                retry_count = 0  # Reset after pause
            else:
                time.sleep(5)


def main():
    """Main entry point"""
    root = tk.Tk()
    app = ProfesorAbeltonGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()


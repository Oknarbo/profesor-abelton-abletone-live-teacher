"""
Profesor Abelton - All-in-One Launcher
Pokreće Server i GUI odjednom
Version: 2.0.0
"""

import os
import sys
import subprocess
import time
import threading
import socket
from pathlib import Path

# Import first-run setup
try:
    from first_run_setup import check_and_install
except ImportError:
    # If running from different directory
    sys.path.insert(0, str(Path(__file__).parent))
    try:
        from first_run_setup import check_and_install
    except ImportError:
        check_and_install = None

# Import Ableton detection + auto-install (best-effort)
try:
    from Utils.ableton_detector import AbletonDetector
except Exception:
    AbletonDetector = None

# Import first-launch wizard (mandatory until completed)
try:
    from GUI.first_launch_wizard import is_setup_complete as wizard_is_setup_complete
    from GUI.first_launch_wizard import run_first_launch_wizard
except Exception:
    wizard_is_setup_complete = None
    run_first_launch_wizard = None

def print_header():
    """Print fancy header"""
    print("=" * 60)
    print("       🎓 PROFESOR ABELTON v2.0.0 🎓")
    print("=" * 60)
    print()

def get_app_root() -> Path:
    """
    Return the application root directory.
    - Source: AI-COPILOT-NOVI/
    - PyInstaller onedir: directory containing ProfesorAbleton.exe
    """
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).parent.resolve()

def check_python():
    """Check Python version"""
    print("[i] Checking Python version...")
    version = sys.version_info
    print(f"    [OK] Python {version.major}.{version.minor}.{version.micro}")
    
    if version.major < 3 or (version.major == 3 and version.minor < 9):
        print("    [!] WARNING: Python 3.9+ recommended")
    print()

def check_dependencies():
    """Check if dependencies are installed"""
    print("[i] Checking dependencies...")
    
    # Core dependencies (required)
    core = ['requests']
    # Optional dependencies (for enhanced features)
    optional = ['speech_recognition', 'pystray']
    
    missing_core = []
    missing_optional = []
    
    # Check core dependencies
    for package in core:
        try:
            __import__(package.replace('-', '_'))
            print(f"    [OK] {package}")
        except ImportError:
            print(f"    [!] {package} - REQUIRED")
            missing_core.append(package)
    
    # Check optional dependencies
    for package in optional:
        try:
            __import__(package.replace('-', '_'))
            print(f"    [OK] {package}")
        except ImportError:
            print(f"    [~] {package} - optional (voice/tray features disabled)")
            missing_optional.append(package)
    
    # Handle missing core dependencies
    if missing_core:
        print()
        print("[!] REQUIRED packages missing!")
        print(f"    pip install {' '.join(missing_core)}")
        print()
        response = input("Install now? (y/n): ")
        if response.lower() == 'y':
            print("[i] Installing core dependencies...")
            try:
                subprocess.run(
                    [sys.executable, '-m', 'pip', 'install'] + missing_core,
                    check=True,
                    capture_output=True
                )
                print("    [OK] Dependencies installed!")
            except:
                print("    [X] Installation error")
                return False
        else:
            print("[X] Cannot continue without core dependencies")
            return False
    
    # Inform about optional dependencies
    if missing_optional:
        print()
        print("[i] Optional features disabled:")
        if 'speech_recognition' in missing_optional:
            print("    - Voice control (text commands still work!)")
        if 'pystray' in missing_optional:
            print("    - System tray (minimize still works!)")
        print()
        print("💡 You can install them later with:")
        print(f"    pip install {' '.join(missing_optional)}")
        print()
    
    print()
    return True

def auto_install_remote_script():
    """
    Best-effort Remote Script installer (does NOT modify RemoteScript contents).
    Installs into Ableton 'User Remote Scripts' directory under the name from config
    (Config/copilot_config.json → ableton.remote_script_name).
    """
    if not AbletonDetector:
        print("[~] Auto-install: detector not available (skipping)")
        return True

    project_root = get_app_root()
    detector = AbletonDetector(project_root=project_root)

    target_dir = detector.best_user_remote_scripts_dir()
    if not target_dir:
        print("[!] Auto-install: Could not determine Ableton User Remote Scripts path.")
        return False

    script_name = detector.remote_script_name()

    # Avoid copying while Ableton is running (can require restart anyway)
    if detector.is_ableton_running():
        print("[!] Ableton Live appears to be running.")
        print("    Please close Ableton, then press Enter to continue install.")
        print("    Or type 'skip' to continue without installing.")
        resp = input("> ").strip().lower()
        if resp == "skip":
            return True

    try:
        from Utils.ableton_detector import install_remote_script_to_all
        ok, msg = install_remote_script_to_all(
            project_root=project_root,
            remote_script_name=script_name,
            overwrite=True,
        )
        if ok:
            print(f"[OK] {msg}")
            print(f"     In Ableton Preferences > Link/Tempo/MIDI:")
            print(f"       Control Surface: {script_name}")
            print("       Input/Output: None")
            print("     Restart Ableton after installing/updating the script.")
            return True
        else:
            print(f"[X] Auto-install failed: {msg}")
            return False
    except Exception as e:
        print(f"[X] Auto-install unexpected error: {e}")
        return False

def start_server():
    """Start Profesor Abelton Server"""
    print("[1/2] Starting Profesor Abelton Server...")
    
    script_dir = get_app_root()

    # In a frozen build, start server in-process (subprocess with sys.executable is unreliable).
    if getattr(sys, "frozen", False):
        try:
            from Server.ai_copilot_server import AICopilotServer  # type: ignore
        except Exception as e:
            print(f"    [X] Cannot import server module: {e}")
            return None

        server = AICopilotServer(config_path=None)

        def _run():
            try:
                server.start()
            except Exception as e:
                print(f"    [X] Server crashed: {e}")

        t = threading.Thread(target=_run, daemon=True)
        t.start()

        # Wait for port to be ready
        print("    [i] Waiting for server to initialize...")
        for _ in range(30):  # ~15s
            time.sleep(0.5)
            try:
                test_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                test_sock.settimeout(1.0)
                test_sock.connect(("localhost", 8766))
                test_sock.close()
                print("    [OK] Server is ready!")
                break
            except Exception:
                pass
        else:
            print("    [X] Server did not become ready.")
            return None

        return server

    server_script = script_dir / "Server" / "ai_copilot_server.py"
    
    if not server_script.exists():
        print(f"    [X] Server script not found: {server_script}")
        return None

    # If something is already listening on the port, avoid starting a second server.
    # This prevents accidentally connecting the GUI to an old server instance.
    try:
        probe = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        probe.settimeout(0.5)
        probe.connect(("localhost", 8766))
        probe.close()
        print("    [!] A server is already running on localhost:8766.")
        print("        Please close the existing server window and re-run the launcher.")
        return None
    except Exception:
        try:
            probe.close()
        except Exception:
            pass
    
    try:
        # Force UTF-8 for server stdout/stderr to avoid Windows cp1250 UnicodeEncodeError
        env = os.environ.copy()
        env.setdefault("PYTHONUTF8", "1")
        env.setdefault("PYTHONIOENCODING", "utf-8")

        # Run server from its own folder so relative paths (e.g. ../Config) work
        server_cwd = str(server_script.parent)

        # On Windows, prefer showing server logs in its own console window.
        # Using PIPE here can also hide errors and risk blocking if buffers fill.
        popen_kwargs = {}
        if sys.platform == "win32":
            popen_kwargs["creationflags"] = subprocess.CREATE_NEW_CONSOLE
            popen_kwargs["stdout"] = None
            popen_kwargs["stderr"] = None
        else:
            popen_kwargs["creationflags"] = 0
            popen_kwargs["stdout"] = subprocess.PIPE
            popen_kwargs["stderr"] = subprocess.PIPE

        # Start server as subprocess
        server_process = subprocess.Popen(
            [sys.executable, str(server_script)],
            cwd=server_cwd,
            env=env,
            **popen_kwargs
        )
        
        print(f"    [OK] Server started (PID: {server_process.pid})")
        if sys.platform == "win32":
            print("    [i] Server running in separate window")
        print("    [i] Waiting for server to initialize...")
        
        # Give server time to start and check if it's ready
        for i in range(20):  # Try for 10 seconds (20 * 0.5s)
            time.sleep(0.5)
            if server_process.poll() is not None:
                # Server exited early — show stderr to help diagnose (redacted by design: no API keys should be printed)
                if server_process.stderr is not None:
                    try:
                        out, err = server_process.communicate(timeout=1)
                    except Exception:
                        out, err = (b"", b"")
                    err_txt = (err or b"").decode("utf-8", errors="replace").strip()
                    if err_txt:
                        print("    [X] Server exited early. Error output:")
                        # Print only first ~30 lines to avoid spam
                        lines = err_txt.splitlines()
                        for line in lines[:30]:
                            print("       " + line)
                    else:
                        print("    [X] Server exited early (no error output captured).")
                else:
                    print("    [X] Server exited early. Check the server console window for errors.")
                return None
            try:
                # Test if server is accepting connections
                test_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                test_sock.settimeout(1.0)
                test_sock.connect(('localhost', 8766))
                test_sock.close()
                print(f"    [OK] Server is ready!")
                break
            except:
                pass
        else:
            print("    [!] Warning: Server may not be ready yet")
        
        return server_process
        
    except Exception as e:
        print(f"    [X] Error: {e}")
        return None

def start_gui():
    """Start Profesor Abelton GUI"""
    print("[2/2] Starting GUI...")
    
    script_dir = get_app_root()
    
    try:
        if getattr(sys, "frozen", False):
            # In frozen build, run GUI in-process.
            from GUI.profesor_ableton_gui import main as gui_main  # type: ignore
            print("    [OK] GUI started (in-process)")
            gui_main()
            return "inprocess"

        gui_dir = script_dir / "GUI"

        # Prefer the newer GUI
        gui_candidates = [
            gui_dir / "profesor_ableton_gui.py",
        ]
        gui_script = next((p for p in gui_candidates if p.exists()), None)
        if not gui_script:
            print("    [X] No GUI script found.")
            for p in gui_candidates:
                print(f"       - {p}")
            return None

        # Windows UX fix:
        # If the GUI is started attached to the current console (PowerShell/cmd),
        # the Tk window often doesn't get its own taskbar button and instead "lives under"
        # the console's taskbar icon (Alt+Tab works, taskbar doesn't).
        # Start the GUI via pythonw.exe (no console) and detach from the parent console.
        popen_kwargs = {}
        exe = sys.executable
        if sys.platform == "win32":
            pyw = Path(sys.executable).with_name("pythonw.exe")
            if pyw.exists():
                exe = str(pyw)
            # DETACHED_PROCESS (0x00000008) + CREATE_NEW_PROCESS_GROUP (0x00000200)
            popen_kwargs["creationflags"] = 0x00000008 | 0x00000200

        gui_process = subprocess.Popen([exe, str(gui_script)], cwd=str(script_dir), **popen_kwargs)
        print(f"    [OK] GUI started: {gui_script.name} (PID: {gui_process.pid})")
        return gui_process
        
    except Exception as e:
        print(f"    [X] Error: {e}")
        return None

def monitor_processes(server_process, gui_process):
    """Monitor and manage processes"""
    print()
    print("=" * 60)
    print("  PROFESOR ABELTON RUNNING!")
    print("=" * 60)
    print()
    print("[i] Server and GUI are running.")
    print("[i] Close GUI window to exit.")
    print("[i] Server will stop automatically.")
    print()
    print("=" * 60)
    print()
    
    try:
        # Wait for GUI to close (subprocess mode)
        if hasattr(gui_process, "wait"):
            gui_process.wait()
        
        print()
        print("[i] GUI closed. Stopping server...")
        
        # Terminate server
        # Subprocess server
        if hasattr(server_process, "poll"):
            if server_process and server_process.poll() is None:
                server_process.terminate()
                try:
                    server_process.wait(timeout=5)
                    print("    [OK] Server stopped")
                except subprocess.TimeoutExpired:
                    server_process.kill()
                    print("    [!] Server force stopped")
        else:
            # In-process server
            try:
                if server_process and hasattr(server_process, "stop"):
                    server_process.stop()
                    print("    [OK] Server stopped")
            except Exception:
                pass
        
    except KeyboardInterrupt:
        print()
        print("[i] User interrupt. Stopping all...")
        
        if hasattr(gui_process, "poll") and gui_process and gui_process.poll() is None:
            gui_process.terminate()
        
        if hasattr(server_process, "poll") and server_process and server_process.poll() is None:
            server_process.terminate()
        elif server_process and hasattr(server_process, "stop"):
            try:
                server_process.stop()
            except Exception:
                pass
        
        print("    [OK] All stopped")

def show_quick_tips():
    """Show quick usage tips"""
    print("💡 QUICK TIPS:")
    print("   • Server: Must be running for AI to work")
    print("   • GUI: Type commands and communicate here")
    print("   • Ableton: Check that ProfesorAbelton is selected in Control Surface")
    print("   • API Keys: Click ⚙️ in GUI to enter keys")
    print("   • Voice: Click 🎤 for voice commands")
    print()

def main():
    """Main launcher"""
    print_header()
    
    # Mandatory first launch wizard
    if run_first_launch_wizard and wizard_is_setup_complete:
        if not wizard_is_setup_complete():
            print("[i] First launch setup required. Opening setup wizard...")
            ok = run_first_launch_wizard(get_app_root())
            if not ok:
                print("[X] Setup wizard not completed. Exiting.")
                return 1
            print("[OK] Setup complete.")
            print()
    else:
        # If wizard import failed, continue (but this should be fixed in packaging).
        pass

    # Check Python
    check_python()
    
    # Check dependencies
    if not check_dependencies():
        input("Press Enter to exit...")
        return 1

    # Install/Update RemoteScript (preferred path)
    print("[i] Checking RemoteScript installation...")
    if not auto_install_remote_script():
        # Fallback to legacy first-run setup if available
        if check_and_install:
            print("[~] Trying legacy installer...")
            if not check_and_install():
                print()
                print("[!] RemoteScript setup incomplete.")
                print("    You can continue, but Ableton won't connect.")
                print()
                response = input("Continue anyway? (y/n): ")
                if response.lower() != 'y':
                    return 1
        else:
            print()
            print("[!] RemoteScript setup incomplete.")
            print("    You can continue, but Ableton won't connect.")
            print()
            response = input("Continue anyway? (y/n): ")
            if response.lower() != 'y':
                return 1
    print()
    
    # Show tips
    show_quick_tips()
    
    # Start server
    server_process = start_server()
    if not server_process:
        print("[X] Cannot start server!")
        input("Press Enter to exit...")
        return 1
    
    # Start GUI
    gui_process = start_gui()
    if not gui_process:
        print("[X] Cannot start GUI!")
        if server_process:
            if hasattr(server_process, "terminate"):
                server_process.terminate()
            elif hasattr(server_process, "stop"):
                try:
                    server_process.stop()
                except Exception:
                    pass
        input("Press Enter to exit...")
        return 1
    
    # Monitor processes
    monitor_processes(server_process, gui_process)
    
    print()
    print("=" * 60)
    print("  Profesor Abelton closed. See you! 🎓")
    print("=" * 60)
    
    return 0

if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except Exception as e:
        print()
        print(f"[X] Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        input("Press Enter to exit...")
        sys.exit(1)


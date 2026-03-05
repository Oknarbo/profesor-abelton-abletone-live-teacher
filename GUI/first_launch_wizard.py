"""
First Launch Wizard (mandatory until completed).

Shows a 5-step setup flow:
1) Welcome
2) Detect Ableton + Remote Scripts path
3) Install / Update Remote Script (one-click)
4) API Keys setup (encrypted storage)
5) Finish + write setup_complete marker
"""

from __future__ import annotations

import os
import sys
import tkinter as tk
from pathlib import Path
from tkinter import messagebox, ttk
from typing import Dict, Optional

# Ensure project root is on path for imports when run directly
if getattr(sys, "frozen", False):
    # In PyInstaller, put resources next to the executable (onedir)
    PROJECT_ROOT = Path(sys.executable).resolve().parent
else:
    PROJECT_ROOT = Path(__file__).parent.parent.resolve()
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

try:
    from Utils.ableton_detector import AbletonDetector, install_remote_script_to_all
except Exception:
    AbletonDetector = None
    install_remote_script_to_all = None

try:
    from Utils.api_key_manager import APIKeyManager
except Exception:
    APIKeyManager = None


def _app_config_dir() -> Path:
    return Path.home() / ".profesor_abelton"


def setup_complete_marker_path() -> Path:
    return _app_config_dir() / "setup_complete"


def is_setup_complete() -> bool:
    return setup_complete_marker_path().exists()


def mark_setup_complete() -> None:
    p = setup_complete_marker_path()
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text("ok\n", encoding="utf-8")


class FirstLaunchWizard(tk.Tk):
    def __init__(self, project_root: Path):
        super().__init__()
        self.project_root = project_root

        self.title("Profesor Abelton - First Launch Setup")
        self.geometry("720x520")
        self.minsize(680, 480)

        self.protocol("WM_DELETE_WINDOW", self._on_close_blocked)

        self.detector = AbletonDetector(project_root=project_root) if AbletonDetector else None
        self.api_key_manager = APIKeyManager() if APIKeyManager else None

        self.remote_scripts_dir: Optional[Path] = None
        self.remote_script_name: str = ""
        self.install_success: bool = False

        self.api_keys: Dict[str, str] = {}

        # Styling
        self.configure(bg="#0a0a0a")
        self._style = ttk.Style(self)
        try:
            self._style.theme_use("clam")
        except Exception:
            pass

        self._style.configure("Wizard.TFrame", background="#0a0a0a")
        self._style.configure("WizardHeader.TFrame", background="#1a1a1a")
        self._style.configure("WizardTitle.TLabel", background="#1a1a1a", foreground="white", font=("Segoe UI", 14, "bold"))
        self._style.configure("WizardSub.TLabel", background="#0a0a0a", foreground="#cccccc", font=("Segoe UI", 10))
        self._style.configure("WizardStep.TLabel", background="#0a0a0a", foreground="#00d4ff", font=("Segoe UI", 11, "bold"))

        self._build_ui()
        self._load_initial_state()
        self._show_step(0)

    # ---------- UI shell ----------
    def _build_ui(self) -> None:
        # Header
        header = ttk.Frame(self, style="WizardHeader.TFrame")
        header.pack(side=tk.TOP, fill=tk.X)

        title = ttk.Label(header, text="FIRST LAUNCH SETUP", style="WizardTitle.TLabel")
        title.pack(side=tk.LEFT, padx=18, pady=14)

        self.step_label = ttk.Label(self, text="", style="WizardStep.TLabel")
        self.step_label.pack(side=tk.TOP, anchor="w", padx=18, pady=(14, 6))

        # Body
        self.body = ttk.Frame(self, style="Wizard.TFrame")
        self.body.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=18, pady=10)

        # Footer
        footer = ttk.Frame(self, style="Wizard.TFrame")
        footer.pack(side=tk.BOTTOM, fill=tk.X, padx=18, pady=14)

        self.back_btn = ttk.Button(footer, text="Back", command=self._back)
        self.back_btn.pack(side=tk.LEFT)

        self.next_btn = ttk.Button(footer, text="Next", command=self._next)
        self.next_btn.pack(side=tk.RIGHT)

        self.finish_btn = ttk.Button(footer, text="Finish", command=self._finish)
        self.finish_btn.pack(side=tk.RIGHT, padx=(0, 10))

        # Steps
        self.steps = [
            self._step_welcome,
            self._step_detect,
            self._step_install,
            self._step_api_keys,
            self._step_finish,
        ]
        self._step_frames: list[tk.Frame] = []

    def _clear_body(self) -> None:
        for child in self.body.winfo_children():
            child.destroy()

    # ---------- State ----------
    def _load_initial_state(self) -> None:
        # Ableton detection
        if self.detector:
            self.remote_scripts_dir = self.detector.best_user_remote_scripts_dir()
            self.remote_script_name = self.detector.remote_script_name()
        else:
            self.remote_scripts_dir = None
            self.remote_script_name = "ProfesorAbelton"

        # API keys
        if self.api_key_manager:
            self.api_keys = self.api_key_manager.load_keys()
        else:
            self.api_keys = {}

        # Install status best-effort (if already installed)
        if self.remote_scripts_dir and self.remote_script_name:
            if (self.remote_scripts_dir / self.remote_script_name / "__init__.py").exists():
                self.install_success = True

    # ---------- Navigation ----------
    def _show_step(self, idx: int) -> None:
        self.current_step = idx
        self._clear_body()

        step_names = [
            "Step 1/5 — Welcome",
            "Step 2/5 — Detect Ableton",
            "Step 3/5 — Install Remote Script",
            "Step 4/5 — API Keys",
            "Step 5/5 — Finish",
        ]
        self.step_label.config(text=step_names[idx])

        # Buttons
        self.back_btn.config(state=("disabled" if idx == 0 else "normal"))
        self.next_btn.config(state=("normal" if idx < 4 else "disabled"))
        self.finish_btn.config(state=("normal" if idx == 4 else "disabled"))

        # Render step
        self.steps[idx]()

        # Step-specific gating
        self._refresh_gating()

    def _refresh_gating(self) -> None:
        # Require successful remote script install before proceeding past step 3
        if self.current_step == 2:
            # On install step: Next disabled until install_success
            self.next_btn.config(state=("normal" if self.install_success else "disabled"))
        if self.current_step == 1:
            # Detect: allow Next always (user can proceed to install)
            self.next_btn.config(state="normal")
        if self.current_step == 3:
            # API keys: allow Next always
            self.next_btn.config(state="normal")

    def _next(self) -> None:
        if self.current_step < 4:
            self._show_step(self.current_step + 1)

    def _back(self) -> None:
        if self.current_step > 0:
            self._show_step(self.current_step - 1)

    # ---------- Steps ----------
    def _step_welcome(self) -> None:
        frame = ttk.Frame(self.body, style="Wizard.TFrame")
        frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(
            frame,
            text="Welcome to Profesor Abelton",
            style="WizardSub.TLabel",
            font=("Segoe UI", 16, "bold"),
            foreground="white",
        ).pack(anchor="w", pady=(8, 10))

        text = (
            "This setup wizard will run once and guide you through:\n"
            "- Detecting Ableton Remote Scripts folder\n"
            "- Installing / updating the control surface script\n"
            "- Saving API keys securely (encrypted per-machine)\n\n"
            "You must complete this wizard before using the app."
        )
        ttk.Label(frame, text=text, style="WizardSub.TLabel", justify="left").pack(anchor="w", pady=(0, 12))

        note = (
            "Tip: If Ableton is running, the installer may ask you to close it,\n"
            "then restart Ableton after installation."
        )
        ttk.Label(frame, text=note, style="WizardSub.TLabel", foreground="#00d4ff", justify="left").pack(anchor="w")

    def _step_detect(self) -> None:
        frame = ttk.Frame(self.body, style="Wizard.TFrame")
        frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(frame, text="Ableton detection", style="WizardSub.TLabel", font=("Segoe UI", 13, "bold"), foreground="white").pack(anchor="w", pady=(6, 10))

        rows = ttk.Frame(frame, style="Wizard.TFrame")
        rows.pack(fill=tk.X, pady=(0, 10))

        def kv(label: str, value: str) -> None:
            r = ttk.Frame(rows, style="Wizard.TFrame")
            r.pack(fill=tk.X, pady=4)
            ttk.Label(r, text=label, style="WizardSub.TLabel", width=24).pack(side=tk.LEFT)
            ttk.Label(r, text=value, style="WizardSub.TLabel").pack(side=tk.LEFT)

        kv("Remote Scripts folder:", str(self.remote_scripts_dir) if self.remote_scripts_dir else "(not detected)")
        kv("Control Surface name:", self.remote_script_name or "(unknown)")
        kv("Ableton running:", "Yes" if (self.detector and self.detector.is_ableton_running()) else "No")

        btns = ttk.Frame(frame, style="Wizard.TFrame")
        btns.pack(anchor="w", pady=(10, 0))

        def refresh() -> None:
            if self.detector:
                self.remote_scripts_dir = self.detector.best_user_remote_scripts_dir()
                self.remote_script_name = self.detector.remote_script_name()
            self._show_step(1)

        ttk.Button(btns, text="Refresh", command=refresh).pack(side=tk.LEFT)

    def _step_install(self) -> None:
        frame = ttk.Frame(self.body, style="Wizard.TFrame")
        frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(frame, text="Install / Update Remote Script", style="WizardSub.TLabel", font=("Segoe UI", 13, "bold"), foreground="white").pack(anchor="w", pady=(6, 10))

        info = (
            "This will copy the bundled `RemoteScript/` folder into your Ableton Remote Scripts directory.\n"
            "Ableton must be restarted after installation."
        )
        ttk.Label(frame, text=info, style="WizardSub.TLabel", justify="left").pack(anchor="w", pady=(0, 12))

        status_frame = ttk.Frame(frame, style="Wizard.TFrame")
        status_frame.pack(fill=tk.X, pady=(0, 10))

        self.install_status = ttk.Label(
            status_frame,
            text=("✅ Installed" if self.install_success else "❌ Not installed yet"),
            style="WizardSub.TLabel",
            foreground=("#00ff88" if self.install_success else "#ff6b35"),
            font=("Segoe UI", 11, "bold"),
        )
        self.install_status.pack(anchor="w")

        def do_install() -> None:
            if not (self.detector and install_remote_script_to_all and self.remote_scripts_dir):
                messagebox.showerror("Error", "Installer not available on this system.")
                return

            if self.detector.is_ableton_running():
                messagebox.showwarning(
                    "Ableton is running",
                    "Ableton Live appears to be running.\n\n"
                    "Please close Ableton, then click Install again.",
                )
                return

            ok, msg = install_remote_script_to_all(
                project_root=self.project_root,
                remote_script_name=self.remote_script_name,
                overwrite=True,
            )
            if ok:
                self.install_success = True
                self.install_status.config(text="✅ Installed", foreground="#00ff88")
                messagebox.showinfo("Success", msg + "\n\nRestart Ableton after this step.")
            else:
                self.install_success = False
                self.install_status.config(text="❌ Not installed yet", foreground="#ff6b35")
                messagebox.showerror("Install failed", msg)

            self._refresh_gating()

        ttk.Button(frame, text="Install / Update", command=do_install).pack(anchor="w", pady=(6, 0))

        hint = "You cannot continue until installation succeeds."
        ttk.Label(frame, text=hint, style="WizardSub.TLabel", foreground="#cccccc").pack(anchor="w", pady=(10, 0))

    def _step_api_keys(self) -> None:
        frame = ttk.Frame(self.body, style="Wizard.TFrame")
        frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(frame, text="API Keys (secure storage)", style="WizardSub.TLabel", font=("Segoe UI", 13, "bold"), foreground="white").pack(anchor="w", pady=(6, 10))

        text = (
            "Keys are stored encrypted on this machine.\n"
            "You can leave them empty if you plan to use a local provider in a future update."
        )
        ttk.Label(frame, text=text, style="WizardSub.TLabel", justify="left").pack(anchor="w", pady=(0, 12))

        if not self.api_key_manager:
            ttk.Label(
                frame,
                text="Secure key storage is not available (missing dependency: cryptography).",
                style="WizardSub.TLabel",
                foreground="#ff6b35",
            ).pack(anchor="w")
            return

        form = ttk.Frame(frame, style="Wizard.TFrame")
        form.pack(fill=tk.X, pady=(0, 10))

        providers = ["GROQ", "CLAUDE"]
        self._key_entries: Dict[str, tk.Entry] = {}

        for i, p in enumerate(providers):
            row = ttk.Frame(form, style="Wizard.TFrame")
            row.pack(fill=tk.X, pady=6)
            ttk.Label(row, text=f"{p}:", style="WizardSub.TLabel", width=12).pack(side=tk.LEFT)
            e = tk.Entry(row, show="•", width=54, bg="#1e1e1e", fg="white", insertbackground="white")
            e.pack(side=tk.LEFT, fill=tk.X, expand=True)
            e.insert(0, self.api_keys.get(p, ""))
            self._key_entries[p] = e

        def save_keys() -> None:
            keys: Dict[str, str] = {}
            for p, e in self._key_entries.items():
                v = e.get().strip()
                if v:
                    keys[p] = v
            try:
                self.api_key_manager.save_keys(keys)
                self.api_keys = keys
                messagebox.showinfo("Saved", "API keys saved securely.")
            except Exception as ex:
                messagebox.showerror("Error", f"Failed to save keys securely:\n{ex}")

        ttk.Button(frame, text="Save keys", command=save_keys).pack(anchor="w")

    def _step_finish(self) -> None:
        frame = ttk.Frame(self.body, style="Wizard.TFrame")
        frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(frame, text="Finish", style="WizardSub.TLabel", font=("Segoe UI", 13, "bold"), foreground="white").pack(anchor="w", pady=(6, 10))

        summary = (
            f"Remote Scripts folder:\n  {self.remote_scripts_dir}\n\n"
            f"Control Surface name:\n  {self.remote_script_name}\n\n"
            "Next steps inside Ableton:\n"
            f"  Preferences → Link/Tempo/MIDI → Control Surface: {self.remote_script_name}\n"
            "  Input/Output: None\n"
            "  Restart Ableton\n"
        )
        ttk.Label(frame, text=summary, style="WizardSub.TLabel", justify="left").pack(anchor="w", pady=(0, 12))

        ttk.Label(
            frame,
            text="Click Finish to complete setup and start the app.",
            style="WizardSub.TLabel",
            foreground="#00d4ff",
        ).pack(anchor="w")

    # ---------- Finish / Close ----------
    def _finish(self) -> None:
        if not self.install_success:
            messagebox.showerror("Setup incomplete", "Remote Script is not installed yet.")
            return
        try:
            mark_setup_complete()
        except Exception as e:
            messagebox.showerror("Error", f"Could not write setup marker:\n{e}")
            return
        self._allow_close = True
        self.destroy()

    def _on_close_blocked(self) -> None:
        # Mandatory wizard: user cannot close without completing.
        messagebox.showwarning(
            "Setup required",
            "You must complete the first launch setup wizard before using the app.",
        )


def run_first_launch_wizard(project_root: Optional[Path] = None) -> bool:
    """
    Returns True when setup is completed.
    """
    pr = project_root or PROJECT_ROOT
    app = FirstLaunchWizard(project_root=pr)
    app.mainloop()
    return is_setup_complete()


if __name__ == "__main__":
    ok = run_first_launch_wizard(PROJECT_ROOT)
    raise SystemExit(0 if ok else 1)


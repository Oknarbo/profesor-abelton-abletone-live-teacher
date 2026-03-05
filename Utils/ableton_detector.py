"""
Ableton Live detection + Remote Script auto-install helpers.

Scope (INSTALL-AGENT):
- Detect Ableton "User Remote Scripts" directory (Windows/macOS best-effort)
- Detect if Ableton is running (best-effort; uses psutil if available)
- Copy repo/bundled RemoteScript folder to target directory

IMPORTANT:
- Do NOT modify RemoteScript contents; only copy/update destination folder.
"""

from __future__ import annotations

import json
import os
import platform
import re
import shutil
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List, Optional, Tuple


try:
    import psutil  # type: ignore
except Exception:  # pragma: no cover
    psutil = None


def _has_any_valid_script_folder(remote_scripts_dir: Path) -> bool:
    """
    Returns True if directory contains at least one subfolder with __init__.py.
    """
    try:
        for child in remote_scripts_dir.iterdir():
            if child.is_dir() and (child / "__init__.py").exists():
                return True
    except Exception:
        return False
    return False


def _detect_existing_preferred_script_name(remote_scripts_dir: Path) -> Optional[str]:
    """
    If user already has a script installed, prefer keeping that name
    (so it appears in Ableton Control Surfaces exactly as before).
    """
    try:
        # Prefer anything that looks like our product first
        preferred_order = []
        for child in remote_scripts_dir.iterdir():
            if not child.is_dir():
                continue
            if not (child / "__init__.py").exists():
                continue
            name = child.name
            preferred_order.append(name)

        # Heuristic preference: Profesor* > AI_Copilot/AICopilot > anything else
        def score(n: str) -> Tuple[int, str]:
            nl = n.lower()
            if "profesor" in nl:
                return (3, nl)
            if "ai_copilot" in nl or "aicopilot" in nl:
                return (2, nl)
            return (1, nl)

        preferred_order.sort(key=lambda n: score(n), reverse=True)
        return preferred_order[0] if preferred_order else None
    except Exception:
        return None


def _parse_ableton_live_dir_sort_key(name: str) -> Tuple[int, int, int, str]:
    """
    Extract a best-effort sort key from folders like:
    - "Live 12"
    - "Live 12 Suite"
    - "Live 12.0.5"
    - "Live 11.3.10"
    Higher is newer.
    """
    m = re.search(r"\bLive\s+(\d+)(?:\.(\d+))?(?:\.(\d+))?\b", name)
    if not m:
        return (0, 0, 0, name.lower())
    major = int(m.group(1) or 0)
    minor = int(m.group(2) or 0)
    patch = int(m.group(3) or 0)
    return (major, minor, patch, name.lower())


def _iter_dirs(path: Path) -> Iterable[Path]:
    try:
        for p in path.iterdir():
            if p.is_dir():
                yield p
    except Exception:
        return


def is_ableton_running() -> bool:
    """
    Best-effort check if Ableton Live is currently running.
    """
    if psutil is None:
        return False
    current_pid = os.getpid()
    try:
        for proc in psutil.process_iter(attrs=["name", "exe"]):
            # Avoid false-positive on our own process name/path (e.g., "ProfesorAbleton.exe")
            try:
                if getattr(proc, "pid", None) == current_pid:
                    continue
            except Exception:
                pass

            name = (proc.info.get("name") or "").lower()
            exe = (proc.info.get("exe") or "").lower()

            # Only treat the actual Ableton Live app as running.
            # Examples: "Ableton Live 12 Suite.exe", "Ableton Live 11.exe"
            if ("ableton live" in name) or ("ableton live" in exe):
                return True
    except Exception:
        return False
    return False


def get_remote_script_name_from_config(project_root: Path) -> str:
    """
    Read Config/copilot_config.json and return ableton.remote_script_name.
    Defaults to 'ProfesorAbelton' if missing.
    """
    cfg = project_root / "Config" / "copilot_config.json"
    try:
        data = json.loads(cfg.read_text(encoding="utf-8"))
        name = data.get("ableton", {}).get("remote_script_name")
        if isinstance(name, str) and name.strip():
            return name.strip()
    except Exception:
        pass
    return "ProfesorAbelton"


def get_source_remotescript_dir(project_root: Path) -> Path:
    """
    Locate bundled/source RemoteScript directory.
    Supports PyInstaller (sys._MEIPASS) and source checkout.
    """
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        base = Path(getattr(sys, "_MEIPASS"))
        return base / "RemoteScript"
    return project_root / "RemoteScript"


def candidate_user_remote_scripts_dirs() -> List[Path]:
    """
    Returns candidate directories where Ableton reads "User Remote Scripts".
    Prefers the Preferences-based location on Windows if available.
    """
    system = platform.system()
    candidates: List[Path] = []

    if system == "Windows":
        # Prefer User Library path first (common and matches many user setups)
        candidates.append(Path.home() / "Documents" / "Ableton" / "User Library" / "Remote Scripts")

        appdata = Path(os.environ.get("APPDATA", "")).expanduser()
        if str(appdata):
            ableton_root = appdata / "Ableton"
            # Common: %APPDATA%\Ableton\Live XX*\Preferences\User Remote Scripts
            for live_dir in sorted(
                (d for d in _iter_dirs(ableton_root) if "live" in d.name.lower()),
                key=lambda p: _parse_ableton_live_dir_sort_key(p.name),
                reverse=True,
            ):
                candidates.append(live_dir / "Preferences" / "User Remote Scripts")

    elif system == "Darwin":
        # Best-effort: preferences folder
        candidates.append(Path.home() / "Library" / "Preferences" / "Ableton")
        # And user library convention used by older scripts
        candidates.append(Path.home() / "Music" / "Ableton" / "User Library" / "Remote Scripts")

    else:
        # Linux (uncommon) best-effort
        candidates.append(Path.home() / "Documents" / "Ableton" / "User Library" / "Remote Scripts")

    return candidates


def find_all_user_remote_scripts_dirs(create_if_missing: bool = True) -> List[Path]:
    """
    Return all existing candidate User Remote Scripts directories.
    If create_if_missing=True, ensure candidates exist and return all of them.
    """
    cands = candidate_user_remote_scripts_dirs()
    if not cands:
        return []

    out: List[Path] = []
    seen = set()

    for p in cands:
        if create_if_missing:
            try:
                p.mkdir(parents=True, exist_ok=True)
            except Exception:
                # If we cannot create it, we'll still include it only if it exists
                pass
        if p.exists():
            key = str(p).lower()
            if key not in seen:
                out.append(p)
                seen.add(key)

    return out


def find_best_user_remote_scripts_dir(create_if_missing: bool = True) -> Optional[Path]:
    """
    Pick the most likely User Remote Scripts directory.
    If nothing exists and create_if_missing=True, creates the top candidate.
    """
    cands = candidate_user_remote_scripts_dirs()

    # Prefer existing directory that already contains scripts
    existing = [p for p in cands if p.exists()]
    for p in existing:
        if _has_any_valid_script_folder(p):
            return p

    # Otherwise, fall back to first existing candidate
    for p in existing:
        return p

    if not create_if_missing or not cands:
        return None

    # Create the first (most preferred) candidate.
    try:
        cands[0].mkdir(parents=True, exist_ok=True)
        return cands[0]
    except Exception:
        return None


def install_remote_script(
    project_root: Path,
    target_user_remote_scripts_dir: Path,
    remote_script_name: str,
    overwrite: bool = True,
) -> Tuple[bool, str]:
    """
    Copy RemoteScript folder to Ableton's User Remote Scripts directory
    under the provided remote_script_name.
    Returns (success, message).
    """
    source_dir = get_source_remotescript_dir(project_root)
    if not source_dir.exists():
        return False, f"RemoteScript folder not found: {source_dir}"

    dest_dir = target_user_remote_scripts_dir / remote_script_name

    try:
        target_user_remote_scripts_dir.mkdir(parents=True, exist_ok=True)
    except Exception as e:
        return False, f"Cannot create target directory: {target_user_remote_scripts_dir} ({e})"

    try:
        # If we're standardizing names, clean up legacy alias folders to avoid
        # multiple Control Surface entries in Ableton for the same product.
        if overwrite:
            legacy_names = ["AICopilot", "AI_Copilot", "ProfesorAbleton"]
            for ln in legacy_names:
                if ln == remote_script_name:
                    continue
                legacy_dir = target_user_remote_scripts_dir / ln
                if legacy_dir.exists():
                    try:
                        shutil.rmtree(legacy_dir)
                    except Exception:
                        # Best-effort cleanup only
                        pass

        if dest_dir.exists():
            if not overwrite:
                return True, f"Remote Script already installed: {dest_dir}"
            shutil.rmtree(dest_dir)
        shutil.copytree(source_dir, dest_dir)
    except Exception as e:
        return False, f"Failed to copy RemoteScript to {dest_dir} ({e})"

    if not (dest_dir / "__init__.py").exists():
        return False, f"Install verification failed: missing __init__.py in {dest_dir}"

    return True, f"Remote Script installed/updated: {dest_dir}"


def install_remote_script_to_all(
    project_root: Path,
    remote_script_name: str,
    overwrite: bool = True,
) -> Tuple[bool, str]:
    """
    Install the Remote Script into all detected User Remote Scripts directories.
    This avoids mismatches where Ableton uses a different 'Live X.Y.Z' preferences folder.
    Returns (success, message).
    """
    dirs = find_all_user_remote_scripts_dirs(create_if_missing=True)
    if not dirs:
        return False, "No Ableton Remote Scripts directories found."

    ok_any = False
    msgs: List[str] = []
    for d in dirs:
        ok, msg = install_remote_script(
            project_root=project_root,
            target_user_remote_scripts_dir=d,
            remote_script_name=remote_script_name,
            overwrite=overwrite,
        )
        msgs.append(msg)
        ok_any = ok_any or ok

    if ok_any:
        return True, " | ".join(msgs)
    return False, " | ".join(msgs)

@dataclass(frozen=True)
class AbletonDetector:
    project_root: Path

    def remote_script_name(self) -> str:
        # Canonical name used across the product.
        # Note: Remote Scripts must be importable Python packages, so we avoid spaces here.
        return get_remote_script_name_from_config(self.project_root)

    def best_user_remote_scripts_dir(self) -> Optional[Path]:
        return find_best_user_remote_scripts_dir(create_if_missing=True)

    def all_user_remote_scripts_dirs(self) -> List[Path]:
        return find_all_user_remote_scripts_dirs(create_if_missing=True)

    def is_ableton_running(self) -> bool:
        return is_ableton_running()


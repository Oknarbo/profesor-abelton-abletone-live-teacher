# -*- mode: python ; coding: utf-8 -*-

from pathlib import Path

block_cipher = None

# PyInstaller provides SPECPATH when executing spec files.
ROOT = Path(globals().get("SPECPATH", ".")).resolve()

datas = [
    (str(ROOT / "Config"), "Config"),
    (str(ROOT / "RemoteScript"), "RemoteScript"),
    (str(ROOT / "Docs"), "Docs"),
    (str(ROOT / "FAQ.md"), "."),
    (str(ROOT / "USER_MANUAL.md"), "."),
    (str(ROOT / "README.md"), "."),
    (str(ROOT / "LICENSE.txt"), "."),
    (str(ROOT / "GUMROAD_README.txt"), "."),
]

hiddenimports = [
    # Ensure bundled modules are present even if imported dynamically
    "Server.ai_copilot_server",
    "GUI.profesor_ableton_gui",
    "GUI.first_launch_wizard",
    "Utils.api_key_manager",
    "Utils.ableton_detector",
    # Optional extras (if present in environment)
    "pystray",
    "PIL",
]

a = Analysis(
    ["launch_profesor_ableton.py"],
    pathex=[str(ROOT)],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="ProfesorAbelton",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,  # windowed app (Gumroad-friendly)
    disable_windowed_traceback=False,
    icon="NONE",
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name="ProfesorAbelton",
)


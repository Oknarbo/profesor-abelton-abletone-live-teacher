#!/usr/bin/env bash
# Strict-ish mode (portable across older shells).
# NOTE: If you run this script via `sh ...`, the shebang is ignored; always use `bash ./build_mac.sh`.
set -e
set -u
{ set -o pipefail; } 2>/dev/null || true

# Profesor Abelton — macOS build script (.app + Gumroad ZIP)
# Run on macOS:
#   chmod +x build_mac.sh
#   ./build_mac.sh
#
# Output:
#   dist/ProfesorAbelton.app
#   release/ProfesorAbelton_macOS_v<version>.zip

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT_DIR"

APP_NAME="ProfesorAbelton"
VERSION="${VERSION:-2.0.0}"
VENV_DIR="${VENV_DIR:-.venv-build-mac}"
PY="$VENV_DIR/bin/python"

echo "[i] Root: $ROOT_DIR"

if [[ ! -f "launch_profesor_ableton.py" ]]; then
  echo "[X] Ne mogu naći launch_profesor_ableton.py. Pokreni skriptu iz root foldera projekta."
  exit 1
fi

if [[ ! -d "$VENV_DIR" ]]; then
  echo "[i] Kreiram build venv: $VENV_DIR"
  python3 -m venv "$VENV_DIR"
fi

echo "[i] Aktiviram venv i instaliram dependencies..."
"$PY" -m pip install --upgrade pip setuptools wheel >/dev/null

# pyaudio je često problematičan na macOS-u (portaudio). Za build nam nije kritičan.
# Instaliraj sve iz requirements.txt osim pyaudio; voice feature može ostati "optional".
TMP_REQ="$(mktemp)"
"$PY" - "$TMP_REQ" <<'PY'
from pathlib import Path
import re, sys

src = Path("requirements.txt").read_text(encoding="utf-8").splitlines()
out = []
for line in src:
    raw = line.strip()
    if not raw or raw.startswith("#"):
        continue
    # remove inline comments (na siguran način)
    raw = re.split(r"\s+#", raw, maxsplit=1)[0].strip()
    if not raw:
        continue
    if raw.lower().startswith("pyaudio"):
        continue
    out.append(raw)
Path(sys.argv[1]).write_text("\n".join(out) + "\n", encoding="utf-8")
PY

"$PY" -m pip install -r "$TMP_REQ"
rm -f "$TMP_REQ"

echo "[i] Building .app (PyInstaller, windowed)..."
rm -rf build dist

"$PY" -m PyInstaller \
  --noconfirm \
  --clean \
  --windowed \
  --name "$APP_NAME" \
  --add-data "Config:Config" \
  --add-data "RemoteScript:RemoteScript" \
  --add-data "Docs:Docs" \
  --add-data "FAQ.md:." \
  --add-data "USER_MANUAL.md:." \
  --add-data "README.md:." \
  --add-data "LICENSE.txt:." \
  --add-data "GUMROAD_README.txt:." \
  --hidden-import "GUI.profesor_ableton_gui" \
  --hidden-import "GUI.first_launch_wizard" \
  --hidden-import "Server.ai_copilot_server" \
  --hidden-import "Utils.api_key_manager" \
  --hidden-import "Utils.ableton_detector" \
  launch_profesor_ableton.py

APP_PATH="dist/$APP_NAME.app"
if [[ ! -d "$APP_PATH" ]]; then
  echo "[X] Build gotov, ali .app nije pronađen: $APP_PATH"
  echo "[DEBUG] Sadržaj dist foldera:"
  ls -la dist/
  exit 1
fi

mkdir -p release
ZIP_PATH="release/${APP_NAME}_macOS_v${VERSION}.zip"

echo "[i] Zipping .app za Gumroad..."
rm -f "$ZIP_PATH"

# ditto je najbolji način za zipanje .app bundle-a (čuva resurse kako treba)
ditto -c -k --sequesterRsrc --keepParent "$APP_PATH" "$ZIP_PATH"

echo ""
echo "[OK] macOS build gotov:"
echo "     $APP_PATH"
echo "     $ZIP_PATH"
echo ""
echo "[i] Napomena:"
echo " - Ako macOS blokira app (Gatekeeper): desni klik → Open → Open."
echo " - Za 'bez upozorenja' treba code signing + notarization (kasnije)."


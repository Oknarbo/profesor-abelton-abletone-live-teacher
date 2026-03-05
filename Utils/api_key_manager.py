"""
Secure API key storage for Profesor Abelton.

Design goals (FAZA 1):
- No plaintext API keys in repo/config/logs
- Encrypted storage at ~/.profesor_abelton/keys.encrypted
- Machine-specific encryption key: Fernet key derived from SHA256(machine_id)
"""

from __future__ import annotations

import base64
import hashlib
import json
import os
import platform
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Optional

from cryptography.fernet import Fernet, InvalidToken


def _safe_makedirs(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def _best_effort_chmod_600(path: Path) -> None:
    # On Windows this may be ignored; still try for POSIX.
    try:
        os.chmod(path, 0o600)
    except Exception:
        pass


def _read_windows_machine_guid() -> Optional[str]:
    if platform.system().lower() != "windows":
        return None
    try:
        import winreg  # type: ignore

        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Cryptography")
        value, _ = winreg.QueryValueEx(key, "MachineGuid")
        return str(value)
    except Exception:
        return None


def _read_linux_machine_id() -> Optional[str]:
    try:
        p = Path("/etc/machine-id")
        if p.exists():
            return p.read_text(encoding="utf-8").strip() or None
    except Exception:
        return None
    return None


def get_machine_id() -> str:
    """
    Return a stable, machine-specific identifier.
    Falls back gracefully if platform-specific sources aren't available.
    """
    mg = _read_windows_machine_guid()
    if mg:
        return mg

    mid = _read_linux_machine_id()
    if mid:
        return mid

    # Fallback: not perfect, but stable enough for typical desktops.
    node = platform.node() or ""
    mac = str(uuid.getnode())
    sys = platform.system() or ""
    rel = platform.release() or ""
    return "|".join([node, mac, sys, rel])


def derive_fernet_key_from_machine_id(machine_id: str) -> bytes:
    """
    Fernet requires a 32-byte urlsafe base64-encoded key.
    Spec requires SHA256(machine_id) → Fernet key.
    """
    digest = hashlib.sha256(machine_id.encode("utf-8")).digest()
    return base64.urlsafe_b64encode(digest)


@dataclass(frozen=True)
class APIKeyManager:
    """
    Stores provider API keys encrypted on disk, per-machine.
    """

    app_dir_name: str = ".profesor_abelton"
    keys_filename: str = "keys.encrypted"

    def _config_dir(self) -> Path:
        return Path.home() / self.app_dir_name

    def keys_path(self) -> Path:
        return self._config_dir() / self.keys_filename

    def _fernet(self) -> Fernet:
        key = derive_fernet_key_from_machine_id(get_machine_id())
        return Fernet(key)

    def load_keys(self) -> Dict[str, str]:
        """
        Load encrypted keys. Returns {} if file doesn't exist or is unreadable.
        Never logs sensitive data.
        """
        path = self.keys_path()
        if not path.exists():
            return {}

        try:
            token = path.read_bytes()
        except Exception:
            return {}

        try:
            data = self._fernet().decrypt(token)
        except InvalidToken:
            # Wrong machine/user or corrupted file.
            return {}
        except Exception:
            return {}

        try:
            obj = json.loads(data.decode("utf-8"))
            if isinstance(obj, dict):
                # Ensure values are strings
                out: Dict[str, str] = {}
                for k, v in obj.items():
                    if isinstance(k, str) and isinstance(v, str):
                        out[k] = v
                return out
        except Exception:
            return {}

        return {}

    def save_keys(self, keys: Dict[str, str]) -> None:
        """
        Encrypt and persist keys. Overwrites existing file atomically.
        """
        cfg_dir = self._config_dir()
        _safe_makedirs(cfg_dir)

        clean: Dict[str, str] = {}
        for k, v in (keys or {}).items():
            if not k or not isinstance(k, str):
                continue
            if not v or not isinstance(v, str):
                continue
            clean[k] = v

        payload = json.dumps(clean, ensure_ascii=False).encode("utf-8")
        token = self._fernet().encrypt(payload)

        target = self.keys_path()
        tmp = target.with_suffix(target.suffix + ".tmp")
        tmp.write_bytes(token)
        _best_effort_chmod_600(tmp)
        tmp.replace(target)
        _best_effort_chmod_600(target)

    def delete_keys_file(self) -> None:
        """
        Deletes the encrypted key file (best effort).
        """
        try:
            self.keys_path().unlink(missing_ok=True)  # type: ignore[arg-type]
        except TypeError:
            # Python < 3.8 fallback
            try:
                if self.keys_path().exists():
                    self.keys_path().unlink()
            except Exception:
                pass
        except Exception:
            pass

    def self_test(self) -> bool:
        """
        Minimal sanity test: encrypt → decrypt roundtrip in memory.
        """
        sample = {"TEST": "secret"}
        payload = json.dumps(sample).encode("utf-8")
        f = self._fernet()
        token = f.encrypt(payload)
        out = json.loads(f.decrypt(token).decode("utf-8"))
        return out == sample


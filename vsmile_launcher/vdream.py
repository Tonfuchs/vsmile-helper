"""Startet V.Smile-Cartridges im Emulator-Kern von V.Dream (``vdream_core.exe``).

Der Kern nimmt den Pfad zur ROM als einziges Argument und braucht kein BIOS.
Er versteht nur rohe ``.bin``-Dateien (kein ``.zip``/``.7z``) und kennt V.Smile
Motion nicht, deshalb prueft ``launch_game`` das vorab und meldet es verstaendlich.
"""

from __future__ import annotations

import os
import re
import subprocess
from pathlib import Path

from .config import resolve_path
from .mame import LaunchError

CORE_NAME = "vdream_core.exe"
# Der Installer legt jede Fassung in einen eigenen Ordner ab: .../V.Dream/v1.4.1/
_VERSION_DIR = re.compile(r"^v(\d+(?:\.\d+)*)$", re.IGNORECASE)


def find_installed_core() -> Path | None:
    """Sucht die neueste installierte ``vdream_core.exe`` im Standardordner des Installers."""
    local = os.environ.get("LOCALAPPDATA", "").strip()
    if not local:
        return None
    base = Path(local) / "FODSOFT" / "V.Dream"

    candidates: list[tuple[tuple[int, ...], Path]] = []
    try:
        for folder in base.iterdir():
            match = _VERSION_DIR.match(folder.name)
            core = folder / CORE_NAME
            if match and core.is_file():
                candidates.append((tuple(int(p) for p in match.group(1).split(".")), core))
    except OSError:
        return None
    return max(candidates)[1] if candidates else None


def build_command(core: str | Path, game_path: str) -> list[str]:
    """Erstellt die Argumentliste fuer den Kern-Aufruf (beide Pfade absolut)."""
    return [str(resolve_path(core)), str(resolve_path(game_path))]


def launch_game(vdream_path: str, game_path: str, console_mode: str = "vsmile") -> subprocess.Popen:
    """Startet den Kern mit der ROM. Wirft LaunchError bei Problemen.

    Ist kein Pfad eingestellt, wird die installierte V.Dream-Fassung gesucht.
    """
    if vdream_path and vdream_path.strip():
        core = resolve_path(vdream_path)
        if not core.is_file():
            raise LaunchError("err_vdream_not_found", path=core)
    else:
        core = find_installed_core()
        if core is None:
            raise LaunchError("err_vdream_not_set")

    if console_mode == "vsmotion":
        raise LaunchError("err_vdream_no_motion")

    game_file = resolve_path(game_path) if game_path and game_path.strip() else None
    if game_file is None or not game_file.is_file():
        raise LaunchError("err_game_not_found", path=game_file or "")
    if game_file.suffix.casefold() != ".bin":
        raise LaunchError("err_vdream_bin_only", name=game_file.name)

    command = build_command(core, str(game_file))

    # Der Kern legt Speicherstaende relativ zum Arbeitsverzeichnis ab (saves/),
    # daher laeuft er im Ordner der Installation, so wie die V.Dream-Oberflaeche.
    try:
        return subprocess.Popen(command, cwd=str(core.parent))
    except OSError as exc:
        raise LaunchError("err_vdream_start_failed", error=exc) from exc

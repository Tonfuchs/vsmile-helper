"""Startet V.Flash-Spiele (CD-Images) im externen V.Flash-Emulator.

MAME kennt die V.Flash (in Europa V.Smile Pro) nicht. Der Launcher ruft deshalb
einen eigenstaendigen Emulator auf, dessen Programmdatei man selbst bereitstellt
(Einstellung ``vflash_path``): ``vflash <image.cue|image.bin>``.
"""

from __future__ import annotations

import subprocess

from .config import resolve_path
from .mame import LaunchError


def build_command(vflash_path: str, game_path: str) -> list[str]:
    """Erstellt die Argumentliste fuer den Emulator-Aufruf (beide Pfade absolut)."""
    return [str(resolve_path(vflash_path)), str(resolve_path(game_path))]


def launch_game(vflash_path: str, game_path: str) -> subprocess.Popen:
    """Startet den Emulator mit dem CD-Image. Wirft LaunchError bei Problemen."""
    if not vflash_path or not vflash_path.strip():
        raise LaunchError("err_vflash_not_set")
    exe = resolve_path(vflash_path)
    if not exe.is_file():
        raise LaunchError("err_vflash_not_found", path=exe)

    game_file = resolve_path(game_path) if game_path and game_path.strip() else None
    if game_file is None or not game_file.is_file():
        raise LaunchError("err_game_not_found", path=game_file or "")

    command = build_command(vflash_path, game_path)

    # Der Emulator sucht seine Boot-ROM (70004.bin) im Arbeitsverzeichnis und in
    # ../vflash-roms/, deshalb laeuft er im eigenen Ordner.
    try:
        return subprocess.Popen(command, cwd=str(exe.parent))
    except OSError as exc:
        raise LaunchError("err_vflash_start_failed", error=exc) from exc

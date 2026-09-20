"""Baut MAME-Kommandozeilen und startet Spiele per subprocess."""

from __future__ import annotations

import subprocess
from typing import Any

from .config import resolve_path
from .i18n import t

CONSOLE_SYSTEMS = {
    "vsmile": "vsmile",
    "vsmotion": "vsmilem",
}


class LaunchError(Exception):
    """Wird ausgeloest, wenn MAME nicht gestartet werden kann.

    Haelt Schluessel und Parameter statt fertigem Text und uebersetzt erst in
    ``__str__``. So zeigt eine gemerkte Fehlermeldung nach einem Sprachwechsel
    die neue Sprache.
    """

    def __init__(self, key: str, **params: Any):
        super().__init__(key)
        self.key = key
        self.params = params

    def __str__(self) -> str:
        return t(self.key, **self.params)


def build_command(
    mame_path: str,
    game_path: str,
    console_mode: str,
    bios_path: str = "",
) -> list[str]:
    """Erstellt die Argumentliste fuer den MAME-Aufruf.

    Relative Pfade werden vom Projektordner aus aufgeloest. MAME laeuft mit
    seinem eigenen Ordner als Arbeitsverzeichnis, deshalb muessen alle Pfade
    absolut uebergeben werden.
    """
    system = CONSOLE_SYSTEMS.get(console_mode, "vsmile")

    command = [str(resolve_path(mame_path)), system]

    if bios_path and bios_path.strip():
        command += ["-rompath", str(resolve_path(bios_path))]

    # Vollstaendiger absoluter Pfad als ein einziges Argument: Popen quotet
    # Leerzeichen und Klammern in langen/deutschen Namen selbst korrekt.
    command += ["-cart", str(resolve_path(game_path))]
    return command


def launch_game(
    mame_path: str,
    game_path: str,
    console_mode: str,
    bios_path: str = "",
) -> subprocess.Popen:
    """Startet MAME mit dem gewaehlten Spiel. Wirft LaunchError bei Problemen."""
    if not mame_path or not mame_path.strip():
        raise LaunchError("err_mame_not_set")
    mame_file = resolve_path(mame_path)
    if not mame_file.is_file():
        raise LaunchError("err_mame_not_found", path=mame_file)

    game_file = resolve_path(game_path) if game_path and game_path.strip() else None
    if game_file is None or not game_file.is_file():
        raise LaunchError("err_game_not_found", path=game_file or "")

    command = build_command(mame_path, game_path, console_mode, bios_path)

    try:
        return subprocess.Popen(command, cwd=str(mame_file.parent))
    except OSError as exc:
        raise LaunchError("err_mame_start_failed", error=exc) from exc

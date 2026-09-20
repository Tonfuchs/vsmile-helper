"""Laden und Speichern der Launcher-Einstellungen in config.json."""

from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path
from typing import Any

# Immer relativ zum Projektordner (nicht zum aktuellen Arbeitsverzeichnis),
# da CWD je nach Startart (IDE, Verknuepfung, Doppelklick) variiert und dort
# unter Umstaenden keine Schreibrechte bestehen.
PROJECT_ROOT = Path(__file__).resolve().parent.parent
CONFIG_FILE = PROJECT_ROOT / "config.json"

DEFAULT_CONFIG: dict[str, Any] = {
    "mame_path": "",
    "bios_path": "",
    "games_path": "",
    "console_mode": "vsmile",  # "vsmile" oder "vsmotion"
    "language": "",  # "de" oder "en"; leer = Systemsprache
}


def resolve_path(value: str | Path, base: Path = PROJECT_ROOT) -> Path:
    """Macht aus einem gespeicherten Pfad einen absoluten.

    Relative Pfade werden vom Projektordner aus aufgeloest (nie vom
    Arbeitsverzeichnis), ``~`` wird expandiert. Symlinks bleiben unangetastet.
    Der Aufrufer prueft vorher, ob ueberhaupt ein Pfad gesetzt ist.
    """
    path = Path(str(value).strip()).expanduser()
    if not path.is_absolute():
        path = base / path
    return Path(os.path.abspath(path))


def to_storable_path(value: str | Path, base: Path = PROJECT_ROOT) -> str:
    """Wandelt einen Pfad in die Form fuer config.json um.

    Liegt er im Projektordner, wird er relativ (mit ``/``) gespeichert, sodass
    der Ordner samt MAME und Spielen verschoben oder auf einen anderen Rechner
    kopiert werden kann. Alles andere bleibt ein absoluter Pfad.
    """
    text = str(value).strip()
    if not text:
        return ""

    absolute = resolve_path(text, base)
    try:
        relative = Path(os.path.realpath(absolute)).relative_to(os.path.realpath(base))
    except ValueError:  # ausserhalb des Projektordners oder anderes Laufwerk
        return absolute.as_posix()
    return relative.as_posix()  # der Projektordner selbst ergibt "."


def load_config(path: Path = CONFIG_FILE) -> dict[str, Any]:
    """Laedt die Konfiguration aus config.json. Legt Defaults an, falls Datei fehlt."""
    if not path.exists():
        return dict(DEFAULT_CONFIG)

    try:
        with path.open("r", encoding="utf-8") as f:
            data = json.load(f)
    except (json.JSONDecodeError, OSError):
        return dict(DEFAULT_CONFIG)

    config = dict(DEFAULT_CONFIG)
    if isinstance(data, dict):
        config.update(data)
    return config


def save_config(config: dict[str, Any], path: Path = CONFIG_FILE) -> None:
    """Speichert die Konfiguration nach config.json.

    Schreibt zuerst in eine temporaere Datei im selben Ordner und ersetzt die
    Zielfile danach atomar. Das vermeidet halb geschriebene Dateien und
    umgeht kurze Schreibsperren, wie sie OneDrive-Synchronisierung auf
    bestehenden Dateien gelegentlich verursacht.
    """
    path.parent.mkdir(parents=True, exist_ok=True)

    fd, tmp_name = tempfile.mkstemp(
        dir=path.parent, prefix=path.stem + ".", suffix=".tmp"
    )
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        os.replace(tmp_name, path)
    except OSError:
        Path(tmp_name).unlink(missing_ok=True)
        raise

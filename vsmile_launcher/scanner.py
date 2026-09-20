"""Scannt den Spiele-Ordner samt aller Unterordner nach unterstuetzten ROM-Dateien."""

from __future__ import annotations

import os
from pathlib import Path
from typing import NamedTuple

from .config import resolve_path

SUPPORTED_EXTENSIONS = {".zip", ".bin", ".iso", ".vsm", ".rom", ".raw"}

# System-/BIOS-Archive, die im ROM-Ordner liegen, aber keine Spiele sind.
# Vergleich erfolgt kleingeschrieben, damit auch VSMILE.ZIP ausgefiltert wird.
IGNORED_FILENAMES = {"vsmile.zip", "vsmilem.zip", "vsmile_cart.zip", "bios german.bin"}


class Game(NamedTuple):
    path: Path  # absoluter Pfad, geht als einziges -cart-Argument an MAME
    label: str  # Pfad relativ zum Spiele-Ordner mit "/", z. B. "V.Smile Motion/DE/x.bin"


def scan_games(games_path: str | Path) -> list[Game]:
    """Gibt alle Spiele im Spiele-Ordner und beliebig tief darunter zurueck.

    Der Ordner wird ohne Rekursion (Stack statt Funktionsaufrufe) durchlaufen,
    die Verschachtelungstiefe ist also nicht begrenzt. Unlesbare Ordner werden
    uebersprungen, verlinkte Ordner einmal gescannt, auch wenn sie im Kreis
    zeigen. Ein relativer ``games_path`` gilt ab dem Projektordner.

    Endungen und Dateinamen werden ohne Beachtung der Gross-/Kleinschreibung
    verglichen. BIOS-Dateien werden ausgefiltert. Gleiche Dateinamen in
    verschiedenen Unterordnern bleiben getrennte Eintraege, unterscheidbar
    ueber ``Game.label``.
    """
    if not str(games_path).strip():
        return []
    root = resolve_path(games_path)
    if not root.is_dir():
        return []

    games: dict[str, Game] = {}
    visited: set[str] = set()
    pending = [root]
    while pending:
        folder = pending.pop()
        real = os.path.normcase(os.path.realpath(folder))
        if real in visited:
            continue
        visited.add(real)

        try:
            with os.scandir(folder) as it:
                entries = list(it)
        except OSError:
            continue

        for entry in entries:
            path = Path(entry.path)
            try:
                if entry.is_dir():
                    pending.append(path)
                    continue
                if not entry.is_file():
                    continue
            except OSError:
                continue

            if entry.name.casefold() in IGNORED_FILENAMES:
                continue
            if path.suffix.casefold() not in SUPPORTED_EXTENSIONS:
                continue

            label = path.relative_to(root).as_posix()
            games.setdefault(label.casefold(), Game(path, label))

    return sorted(games.values(), key=lambda g: g.label.casefold())

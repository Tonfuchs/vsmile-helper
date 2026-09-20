"""Scannt den Spiele-Ordner samt aller Unterordner nach unterstuetzten ROM-Dateien."""

from __future__ import annotations

import os
import re
from pathlib import Path
from typing import NamedTuple

from .config import resolve_path

SUPPORTED_EXTENSIONS = {".zip", ".bin", ".iso", ".vsm", ".rom", ".raw", ".cue"}

# Cartridges laufen unter MAME, CD-Images (V.Flash / V.Smile Pro) im externen
# V.Flash-Emulator.
SYSTEM_CART = "cart"
SYSTEM_VFLASH = "vflash"

# Jeder rohe CD-Sektor (2352 Byte) beginnt mit diesem Sync-Muster. Ein
# Cartridge-Dump faengt praktisch nie so an, das .bin verraet sich also selbst.
CD_SYNC = bytes([0x00] + [0xFF] * 10 + [0x00])
_CUE_FILE = re.compile(r'^\s*FILE\s+(?:"([^"]+)"|(\S+))', re.IGNORECASE | re.MULTILINE)

# System-/BIOS-Archive, die im ROM-Ordner liegen, aber keine Spiele sind.
# Vergleich erfolgt kleingeschrieben, damit auch VSMILE.ZIP ausgefiltert wird.
IGNORED_FILENAMES = {"vsmile.zip", "vsmilem.zip", "vsmile_cart.zip", "bios german.bin"}


class Game(NamedTuple):
    path: Path  # absoluter Pfad, geht als einziges -cart-Argument an MAME
    label: str  # Pfad relativ zum Spiele-Ordner mit "/", z. B. "V.Smile Motion/DE/x.bin"
    system: str = SYSTEM_CART  # SYSTEM_CART (MAME) oder SYSTEM_VFLASH (CD-Image)


def _norm(path: Path) -> str:
    return os.path.normcase(os.path.abspath(path))


def is_cd_image(path: Path) -> bool:
    """True, wenn die Datei mit dem Sync-Muster eines rohen CD-Sektors beginnt."""
    try:
        with path.open("rb") as f:
            return f.read(len(CD_SYNC)) == CD_SYNC
    except OSError:
        return False


def _cue_tracks(cue: Path) -> set[str]:
    """Dateien, die zu einer .cue gehoeren und deshalb nicht einzeln erscheinen sollen.

    Das ist das gleichnamige .bin plus alles, was die .cue per ``FILE`` nennt.
    """
    tracks = {_norm(cue.with_suffix(".bin"))}
    try:
        with cue.open("r", encoding="utf-8", errors="replace") as f:
            text = f.read(65536)
    except OSError:
        return tracks
    for quoted, bare in _CUE_FILE.findall(text):
        tracks.add(_norm(cue.parent / (quoted or bare)))
    return tracks


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

    CD-Images (``.cue`` oder ein ``.bin`` mit CD-Sync-Muster) tragen
    ``system == SYSTEM_VFLASH``. Ein ``.bin``, das zu einer ``.cue`` gehoert,
    wird ausgeblendet, damit das Spiel nur einmal in der Liste steht.
    """
    if not str(games_path).strip():
        return []
    root = resolve_path(games_path)
    if not root.is_dir():
        return []

    found: list[tuple[Path, str]] = []
    cue_owned: set[str] = set()  # Dateien, die eine .cue schon vertritt
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

            if path.suffix.casefold() == ".cue":
                cue_owned |= _cue_tracks(path)
            found.append((path, path.relative_to(root).as_posix()))

    games: dict[str, Game] = {}
    for path, label in found:
        suffix = path.suffix.casefold()
        if suffix != ".cue" and _norm(path) in cue_owned:
            continue
        is_cd = suffix == ".cue" or (suffix == ".bin" and is_cd_image(path))
        system = SYSTEM_VFLASH if is_cd else SYSTEM_CART
        games.setdefault(label.casefold(), Game(path, label, system))

    return sorted(games.values(), key=lambda g: g.label.casefold())

"""Setzt __version__ in main.py auf die neue Versionsnummer (fuer den Release-Workflow).

Aufruf:  python .github/scripts/set_version.py 1.1.0

Bricht mit Fehlercode 1 ab, wenn die Nummer nicht "X.Y.Z" ist oder nicht groesser
als die aktuelle Version ist. Gibt bei Erfolg "<alt> -> <neu>" aus.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

MAIN_PY = Path(__file__).resolve().parents[2] / "main.py"
VERSION_RE = re.compile(r"^\d+\.\d+\.\d+$")
ASSIGNMENT_RE = re.compile(r'^(__version__\s*=\s*)"([^"]*)"', re.MULTILINE)


def as_tuple(version: str) -> tuple[int, ...]:
    return tuple(int(part) for part in version.split("."))


def main(argv: list[str]) -> int:
    if len(argv) != 2 or not VERSION_RE.match(argv[1]):
        print('Versionsnummer muss die Form "X.Y.Z" haben, z. B. 1.1.0 (ohne "v").', file=sys.stderr)
        return 1
    new = argv[1]

    source = MAIN_PY.read_text(encoding="utf-8")
    match = ASSIGNMENT_RE.search(source)
    if not match:
        print(f"__version__ nicht in {MAIN_PY.name} gefunden.", file=sys.stderr)
        return 1
    old = match.group(2)

    if not VERSION_RE.match(old) or as_tuple(new) <= as_tuple(old):
        print(f"Neue Version {new} muss groesser sein als die aktuelle ({old}).", file=sys.stderr)
        return 1

    MAIN_PY.write_text(
        ASSIGNMENT_RE.sub(lambda m: f'{m.group(1)}"{new}"', source, count=1),
        encoding="utf-8",
        newline="",  # Zeilenenden der Datei nicht veraendern
    )
    print(f"{old} -> {new}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))

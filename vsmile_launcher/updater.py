"""Update-Pruefung ueber die GitHub-REST-API.

Beim App-Start fragt ``UpdateCheck`` in einem Hintergrund-Thread das neueste
Release des Repos ab und vergleicht dessen Tag mit der lokalen Version. Die GUI
wird dabei nie blockiert; Netzwerkfehler (offline, Rate-Limit, kein Release
vorhanden) fuehren still zu "kein Update", damit der Start nie stoert.

tkinter ist nicht thread-sicher: Der Thread setzt nur ``result`` und ein Event,
die GUI fragt ``finished`` per ``after`` ab und baut die Meldung selbst.
"""

from __future__ import annotations

import http.client
import json
import re
import threading
import urllib.request
import webbrowser
from dataclasses import dataclass
from typing import Callable

GITHUB_OWNER = "Tonfuchs"
GITHUB_REPO = "vsmile-helper"
LATEST_RELEASE_API = f"https://api.github.com/repos/{GITHUB_OWNER}/{GITHUB_REPO}/releases/latest"
RELEASES_PAGE = f"https://github.com/{GITHUB_OWNER}/{GITHUB_REPO}/releases/latest"

REQUEST_TIMEOUT = 8  # Sekunden
MAX_RESPONSE_BYTES = 1_000_000

_VERSION_RE = re.compile(r"^\s*[vV]?(\d+(?:\.\d+)*)")


@dataclass(frozen=True)
class UpdateInfo:
    version: str  # ohne fuehrendes "v", z. B. "1.1.0"
    url: str  # Release-Seite auf GitHub


def parse_version(text: str) -> tuple[int, ...] | None:
    """Liest "v1.2.3" oder "1.2" als Zahlentupel. Alles andere -> None.

    Zusaetze hinter der Zahl ("1.2.0-beta") werden ignoriert.
    """
    match = _VERSION_RE.match(text)
    if not match:
        return None
    return tuple(int(part) for part in match.group(1).split("."))


def is_newer(remote: tuple[int, ...], local: tuple[int, ...]) -> bool:
    # Auf gleiche Laenge auffuellen, damit (1, 0) und (1, 0, 0) gleich sind.
    size = max(len(remote), len(local))
    pad = lambda v: v + (0,) * (size - len(v))  # noqa: E731
    return pad(remote) > pad(local)


def fetch_latest_release(timeout: float = REQUEST_TIMEOUT) -> dict:
    """Holt die JSON-Antwort von ``/releases/latest`` (Entwuerfe und Pre-Releases zaehlen dort nicht)."""
    request = urllib.request.Request(
        LATEST_RELEASE_API,
        headers={
            "Accept": "application/vnd.github+json",
            # GitHub lehnt Anfragen ohne User-Agent ab.
            "User-Agent": f"{GITHUB_REPO}-update-check",
        },
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return json.loads(response.read(MAX_RESPONSE_BYTES))


def _release_url(release: dict) -> str:
    # Nur Links auf das eigene Repo uebernehmen, sonst die feste Release-Seite.
    url = release.get("html_url")
    if isinstance(url, str) and url.startswith(f"https://github.com/{GITHUB_OWNER}/{GITHUB_REPO}/"):
        return url
    return RELEASES_PAGE


def check_for_update(
    local_version: str,
    fetch: Callable[[], dict] | None = None,
) -> UpdateInfo | None:
    """Liefert ``UpdateInfo``, wenn auf GitHub ein neueres Release existiert, sonst None."""
    local = parse_version(local_version)
    if local is None:
        return None

    try:
        release = (fetch or fetch_latest_release)()
    except (OSError, http.client.HTTPException, ValueError):
        # OSError deckt URLError, HTTPError (404 = noch kein Release, 403 = Rate-Limit)
        # und Timeouts ab; ValueError kaputtes JSON oder falsche Kodierung.
        return None

    if not isinstance(release, dict):
        return None
    tag = release.get("tag_name")
    remote = parse_version(tag) if isinstance(tag, str) else None
    if remote is None or not is_newer(remote, local):
        return None
    return UpdateInfo(version=".".join(map(str, remote)), url=_release_url(release))


class UpdateCheck:
    """Startet die Pruefung sofort im Hintergrund; Ergebnis spaeter abholen."""

    def __init__(self, local_version: str, fetch: Callable[[], dict] | None = None):
        self.result: UpdateInfo | None = None
        self._done = threading.Event()
        threading.Thread(
            target=self._run,
            args=(local_version, fetch),
            name="update-check",
            daemon=True,
        ).start()

    @property
    def finished(self) -> bool:
        return self._done.is_set()

    def _run(self, local_version: str, fetch: Callable[[], dict] | None) -> None:
        try:
            self.result = check_for_update(local_version, fetch)
        finally:
            self._done.set()


def open_release_page(info: UpdateInfo) -> bool:
    """Oeffnet die Release-Seite im Standardbrowser. False, wenn das nicht klappte."""
    try:
        return webbrowser.open(info.url)
    except webbrowser.Error:
        return False

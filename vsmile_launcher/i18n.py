"""Mehrsprachigkeit (Deutsch / English) fuer alle GUI-Texte und Fehlermeldungen.

Alle sichtbaren Texte laufen ueber ``t("schluessel", ...)``. Die aktive Sprache
wird mit ``set_language`` gesetzt; fehlt ein Schluessel in der aktiven Sprache,
wird auf Englisch und zuletzt auf den Schluessel selbst zurueckgefallen.
"""

from __future__ import annotations

import locale
import os
from typing import Any

# Kuerzel -> Anzeigename. Die Namen bleiben bewusst unuebersetzt, damit man die
# eigene Sprache auch dann findet, wenn die Oberflaeche gerade in einer
# unbekannten Sprache steht.
LANGUAGES: dict[str, str] = {
    "de": "Deutsch",
    "en": "English",
}
DEFAULT_LANGUAGE = "en"

TRANSLATIONS: dict[str, dict[str, str]] = {
    "de": {
        # Hauptfenster
        "language_label": "Sprache:",
        "console_label": "Konsole:",
        "emulator_label": "Emulator:",
        "emulator_mame": "MAME",
        "emulator_vdream": "V.Dream",
        "console_vsmile": "V.Smile (Standard)",
        "console_vsmotion": "V.Smile Motion",
        "console_vflash": "V.Flash (experimentell)",
        "game_tag_vflash": "[V.Flash] {name}",
        "btn_settings": "Einstellungen",
        "btn_refresh": "Aktualisieren",
        "games_list_title": "Spiele",
        "no_game_selected": "Kein Spiel ausgewählt",
        "selected_game": "Ausgewählt: {name}",
        "btn_start": "Starten",
        # Statuszeile
        "status_no_games_path": "Kein Spiele-Ordner eingestellt. Bitte in den Einstellungen festlegen.",
        "status_games_path_missing": "Spiele-Ordner nicht gefunden: {path}",
        "status_no_games_found": "Keine Spiele gefunden in: {path}",
        "status_games_found": "{count} Spiel(e) gefunden.",
        "status_started": "Gestartet: {name} ({console})",
        "status_error": "Fehler: {error}",
        "status_save_failed": "Einstellungen konnten nicht gespeichert werden: {error}",
        "status_browser_failed": "Browser konnte nicht geöffnet werden. Release-Seite: {url}",
        # Update-Hinweis
        "update_available": "Neue Version verfügbar! (v{version})",
        "update_download": "Herunterladen",
        # Einstellungsdialog
        "settings_title": "Einstellungen",
        "settings_mame": "mame.exe:",
        "settings_bios": "BIOS-Ordner:",
        "settings_games": "Spiele-Ordner:",
        "settings_vflash": "vflash.exe:",
        "settings_vdream": "vdream_core.exe:",
        "settings_browse": "Durchsuchen",
        "settings_save": "Speichern",
        "settings_cancel": "Abbrechen",
        "settings_hint": (
            "Pfade innerhalb des Projektordners werden relativ gespeichert, "
            "damit sich der Ordner verschieben lässt. vflash.exe ist optional und "
            "nur für V.Flash-CDs nötig; MAME kann sie nicht starten. "
            "vdream_core.exe ist optional; leer heißt: die installierte V.Dream-Fassung suchen."
        ),
        "dialog_select_mame": "mame.exe auswählen",
        "dialog_select_bios": "BIOS-Ordner auswählen",
        "dialog_select_games": "Spiele-Ordner auswählen",
        "dialog_select_vflash": "vflash.exe auswählen",
        "dialog_select_vdream": "vdream_core.exe auswählen",
        "filetype_mame": "MAME-Programm",
        "filetype_vflash": "V.Flash-Emulator",
        "filetype_vdream": "V.Dream-Kern",
        "filetype_all": "Alle Dateien",
        # Fehler beim Starten von MAME
        "err_mame_not_set": "Kein Pfad zu mame.exe eingestellt. Bitte in den Einstellungen festlegen.",
        "err_mame_not_found": "mame.exe wurde nicht gefunden: {path}",
        "err_game_not_found": "Spieldatei wurde nicht gefunden: {path}",
        "err_mame_start_failed": "MAME konnte nicht gestartet werden: {error}",
        # Fehler beim Starten des V.Flash-Emulators
        "err_vflash_not_set": (
            "Für V.Flash-CDs fehlt der Pfad zu vflash.exe (V.Flash-Emulator). "
            "Bitte in den Einstellungen festlegen."
        ),
        "err_vflash_not_found": "vflash.exe wurde nicht gefunden: {path}",
        "err_vflash_start_failed": "Der V.Flash-Emulator konnte nicht gestartet werden: {error}",
        # Fehler beim Starten von V.Dream
        "err_vdream_not_set": (
            "V.Dream wurde nicht gefunden. Bitte den Pfad zu vdream_core.exe in den "
            "Einstellungen festlegen oder MAME als Emulator wählen."
        ),
        "err_vdream_not_found": "vdream_core.exe wurde nicht gefunden: {path}",
        "err_vdream_no_motion": (
            "V.Dream kann V.Smile Motion nicht starten. Bitte MAME als Emulator wählen."
        ),
        "err_vdream_bin_only": (
            "V.Dream startet nur .bin-Dateien, nicht: {name}. Bitte MAME als Emulator wählen."
        ),
        "err_vdream_start_failed": "V.Dream konnte nicht gestartet werden: {error}",
    },
    "en": {
        # Main window
        "language_label": "Language:",
        "console_label": "Console:",
        "emulator_label": "Emulator:",
        "emulator_mame": "MAME",
        "emulator_vdream": "V.Dream",
        "console_vsmile": "V.Smile (Standard)",
        "console_vsmotion": "V.Smile Motion",
        "console_vflash": "V.Flash (experimental)",
        "game_tag_vflash": "[V.Flash] {name}",
        "btn_settings": "Settings",
        "btn_refresh": "Refresh",
        "games_list_title": "Games",
        "no_game_selected": "No game selected",
        "selected_game": "Selected: {name}",
        "btn_start": "Start",
        # Status line
        "status_no_games_path": "No games folder configured. Please set one in the settings.",
        "status_games_path_missing": "Games folder not found: {path}",
        "status_no_games_found": "No games found in: {path}",
        "status_games_found": "{count} game(s) found.",
        "status_started": "Started: {name} ({console})",
        "status_error": "Error: {error}",
        "status_save_failed": "Settings could not be saved: {error}",
        "status_browser_failed": "Could not open the browser. Release page: {url}",
        # Update notice
        "update_available": "New version available! (v{version})",
        "update_download": "Download",
        # Settings dialog
        "settings_title": "Settings",
        "settings_mame": "mame.exe:",
        "settings_bios": "BIOS folder:",
        "settings_games": "Games folder:",
        "settings_vflash": "vflash.exe:",
        "settings_vdream": "vdream_core.exe:",
        "settings_browse": "Browse",
        "settings_save": "Save",
        "settings_cancel": "Cancel",
        "settings_hint": (
            "Paths inside the project folder are stored relative to it, "
            "so the folder can be moved freely. vflash.exe is optional and only "
            "needed for V.Flash CDs; MAME cannot run them. "
            "vdream_core.exe is optional; empty means: look for the installed V.Dream."
        ),
        "dialog_select_mame": "Select mame.exe",
        "dialog_select_bios": "Select BIOS folder",
        "dialog_select_games": "Select games folder",
        "dialog_select_vflash": "Select vflash.exe",
        "dialog_select_vdream": "Select vdream_core.exe",
        "filetype_mame": "MAME executable",
        "filetype_vflash": "V.Flash emulator",
        "filetype_vdream": "V.Dream core",
        "filetype_all": "All files",
        # Errors when launching MAME
        "err_mame_not_set": "No path to mame.exe configured. Please set it in the settings.",
        "err_mame_not_found": "mame.exe was not found: {path}",
        "err_game_not_found": "Game file was not found: {path}",
        "err_mame_start_failed": "MAME could not be started: {error}",
        # Errors when launching the V.Flash emulator
        "err_vflash_not_set": (
            "No path to vflash.exe (V.Flash emulator) configured for V.Flash CDs. "
            "Please set it in the settings."
        ),
        "err_vflash_not_found": "vflash.exe was not found: {path}",
        "err_vflash_start_failed": "The V.Flash emulator could not be started: {error}",
        # Errors when launching V.Dream
        "err_vdream_not_set": (
            "V.Dream was not found. Please set the path to vdream_core.exe in the "
            "settings or choose MAME as the emulator."
        ),
        "err_vdream_not_found": "vdream_core.exe was not found: {path}",
        "err_vdream_no_motion": (
            "V.Dream cannot run V.Smile Motion. Please choose MAME as the emulator."
        ),
        "err_vdream_bin_only": (
            "V.Dream only runs .bin files, not: {name}. Please choose MAME as the emulator."
        ),
        "err_vdream_start_failed": "V.Dream could not be started: {error}",
    },
}

_current = DEFAULT_LANGUAGE


def detect_system_language() -> str:
    """Leitet die Sprache aus der Systemumgebung ab, sonst Englisch."""
    candidates: list[str] = []
    try:
        candidates.append(locale.getlocale()[0] or "")
    except (ValueError, TypeError):
        pass
    candidates += [os.environ.get(name, "") for name in ("LC_ALL", "LC_MESSAGES", "LANG")]

    for name in candidates:
        lowered = name.lower()
        # Windows liefert "German_Germany", POSIX "de_DE.UTF-8".
        if lowered.startswith(("de", "german")):
            return "de"
        if lowered.startswith(("en", "english")):
            return "en"
    return DEFAULT_LANGUAGE


def set_language(code: str | None) -> str:
    """Setzt die aktive Sprache. Unbekannte oder leere Kuerzel -> Systemsprache.

    Gibt das tatsaechlich verwendete Kuerzel zurueck.
    """
    global _current
    _current = code if code in LANGUAGES else detect_system_language()
    return _current


def get_language() -> str:
    return _current


def t(key: str, **params: Any) -> str:
    """Liefert den Text zum Schluessel in der aktiven Sprache."""
    text = TRANSLATIONS.get(_current, {}).get(key)
    if text is None:
        text = TRANSLATIONS[DEFAULT_LANGUAGE].get(key, key)
    return text.format(**params) if params else text

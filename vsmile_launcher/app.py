"""Hauptfenster des VSmile-MAME-Launcher."""

from __future__ import annotations

from typing import Callable

import customtkinter as ctk

from . import config as config_module
from . import i18n, mame, updater
from .i18n import t
from .scanner import Game, scan_games
from .settings_dialog import SettingsDialog

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

CONSOLE_MODES = ("vsmile", "vsmotion")
UPDATE_POLL_MS = 300


def console_label(mode: str) -> str:
    return t(f"console_{mode}")


class LauncherApp(ctk.CTk):
    def __init__(self, version: str):
        super().__init__()

        self.title("VSmile-MAME-Launcher")
        self.geometry("680x540")
        self.minsize(520, 420)

        self.config_data = config_module.load_config()
        self.config_data["language"] = i18n.set_language(self.config_data.get("language"))
        self.games: list[Game] = []
        self.selected_game: Game | None = None
        # Die Statuszeile merkt sich eine Funktion statt Text, damit sie nach
        # einem Sprachwechsel neu uebersetzt werden kann.
        self._status_text: Callable[[], str] = lambda: ""
        # Ergebnis der Update-Pruefung; _build_layout zeichnet die Meldung daraus
        # neu, weil ein Sprachwechsel das ganze Fenster neu aufbaut.
        self.update_info: updater.UpdateInfo | None = None
        self.update_bar: ctk.CTkFrame | None = None

        self._build_layout()
        self.refresh_game_list()

        # Die Abfrage laeuft im Hintergrund, die GUI fragt das Ergebnis nur ab.
        self._update_check = updater.UpdateCheck(version)
        self.after(UPDATE_POLL_MS, self._poll_update_check)

    def _build_layout(self) -> None:
        for widget in self.winfo_children():
            widget.destroy()
        self.update_bar = None

        # Kopfzeile: Konsolen-Modus + Einstellungen
        header = ctk.CTkFrame(self)
        header.pack(fill="x", padx=15, pady=(15, 5))

        ctk.CTkLabel(header, text=t("console_label")).pack(side="left", padx=(5, 5))

        mode = self.config_data.get("console_mode", "vsmile")
        if mode not in CONSOLE_MODES:
            mode = "vsmile"
        self.mode_var = ctk.StringVar(value=console_label(mode))
        mode_menu = ctk.CTkOptionMenu(
            header,
            values=[console_label(m) for m in CONSOLE_MODES],
            variable=self.mode_var,
            command=self._on_mode_change,
        )
        mode_menu.pack(side="left", padx=5)

        settings_btn = ctk.CTkButton(header, text=t("btn_settings"), command=self._open_settings)
        settings_btn.pack(side="right", padx=5)

        refresh_btn = ctk.CTkButton(header, text=t("btn_refresh"), command=self.refresh_game_list)
        refresh_btn.pack(side="right", padx=5)

        # Spieleliste
        self.list_frame = ctk.CTkScrollableFrame(self, label_text=t("games_list_title"))
        self.list_frame.pack(fill="both", expand=True, padx=15, pady=5)

        # Start-Leiste
        footer = ctk.CTkFrame(self)
        footer.pack(fill="x", padx=15, pady=(5, 5))

        self.selected_label = ctk.CTkLabel(footer, text="", anchor="w")
        self.selected_label.pack(side="left", padx=5, fill="x", expand=True)

        self.start_btn = ctk.CTkButton(footer, text=t("btn_start"), command=self._start_selected)
        self.start_btn.pack(side="right", padx=5)

        # Statuszeile + Sprachauswahl
        bottom = ctk.CTkFrame(self, fg_color="transparent")
        bottom.pack(fill="x", padx=15, pady=(0, 10))

        self.status_label = ctk.CTkLabel(bottom, text="", text_color="gray70", anchor="w")
        self.status_label.pack(side="left", padx=5, fill="x", expand=True)

        language_menu = ctk.CTkOptionMenu(
            bottom,
            values=list(i18n.LANGUAGES.values()),
            variable=ctk.StringVar(value=i18n.LANGUAGES[i18n.get_language()]),
            command=self._on_language_change,
            width=110,
        )
        language_menu.pack(side="right", padx=5)
        ctk.CTkLabel(bottom, text=t("language_label")).pack(side="right", padx=(5, 0))

        self._update_selection_ui()
        self._show_status()
        self._render_update_bar()

    def _poll_update_check(self) -> None:
        if not self._update_check.finished:
            self.after(UPDATE_POLL_MS, self._poll_update_check)
            return
        if self._update_check.result is not None:
            self.update_info = self._update_check.result
            self._render_update_bar()

    def _render_update_bar(self) -> None:
        """Schmale Zeile ganz unten, nur sichtbar wenn ein neueres Release existiert."""
        if self.update_bar is not None:
            self.update_bar.destroy()
            self.update_bar = None
        if self.update_info is None:
            return

        bar = ctk.CTkFrame(self, fg_color="transparent")
        bar.pack(fill="x", padx=15, pady=(0, 10))
        ctk.CTkLabel(
            bar,
            text=t("update_available", version=self.update_info.version),
            text_color="gray70",
            anchor="w",
        ).pack(side="left", padx=5)
        ctk.CTkButton(
            bar,
            text=t("update_download"),
            width=100,
            height=24,
            command=self._open_release_page,
        ).pack(side="left", padx=5)
        self.update_bar = bar

    def _open_release_page(self) -> None:
        info = self.update_info
        if info is not None and not updater.open_release_page(info):
            self._set_status(lambda: t("status_browser_failed", url=info.url))

    def _on_mode_change(self, label: str) -> None:
        for mode in CONSOLE_MODES:
            if console_label(mode) == label:
                self.config_data["console_mode"] = mode
                break
        self._save_config_safely()

    def _on_language_change(self, name: str) -> None:
        code = next((c for c, n in i18n.LANGUAGES.items() if n == name), i18n.DEFAULT_LANGUAGE)
        self.config_data["language"] = i18n.set_language(code)
        self._save_config_safely()
        # Erst nach dem Callback umbauen: das Dropdown, das ihn gerade ausfuehrt,
        # wird dabei zerstoert.
        self.after(10, self._rebuild_ui)

    def _rebuild_ui(self) -> None:
        self._build_layout()
        self._render_game_list()

    def _open_settings(self) -> None:
        SettingsDialog(self, self.config_data, self._on_settings_saved)

    def _on_settings_saved(self, new_config: dict) -> None:
        self.config_data = new_config
        self._save_config_safely()
        self.refresh_game_list()

    def _save_config_safely(self) -> None:
        try:
            config_module.save_config(self.config_data)
        except OSError as exc:
            self._set_status(lambda err=exc: t("status_save_failed", error=err))

    def refresh_game_list(self) -> None:
        games_path = self.config_data.get("games_path", "")
        self.games = scan_games(games_path)
        self.selected_game = None
        self._render_game_list()
        self._update_selection_ui()

        if not games_path.strip():
            self._set_status(lambda: t("status_no_games_path"))
            return

        folder = config_module.resolve_path(games_path)
        if not folder.is_dir():
            self._set_status(lambda: t("status_games_path_missing", path=folder))
        elif not self.games:
            self._set_status(lambda: t("status_no_games_found", path=folder))
        else:
            count = len(self.games)
            self._set_status(lambda: t("status_games_found", count=count))

    def _render_game_list(self) -> None:
        for widget in self.list_frame.winfo_children():
            widget.destroy()

        for game in self.games:
            row = ctk.CTkFrame(self.list_frame, fg_color="transparent")
            row.pack(fill="x", pady=2)

            # Der Pfad relativ zum Spiele-Ordner unterscheidet gleichnamige
            # Dateien aus verschiedenen Unterordnern (z. B. .../DE/ und .../EN/).
            label = ctk.CTkButton(
                row,
                text=game.label,
                anchor="w",
                fg_color="gray25",
                hover_color="gray35",
                command=lambda g=game: self._select_game(g),
            )
            label.pack(side="left", fill="x", expand=True, padx=2)

    def _select_game(self, game: Game) -> None:
        self.selected_game = game
        self._update_selection_ui()

    def _update_selection_ui(self) -> None:
        if self.selected_game:
            self.selected_label.configure(text=t("selected_game", name=self.selected_game.label))
            self.start_btn.configure(state="normal")
        else:
            self.selected_label.configure(text=t("no_game_selected"))
            self.start_btn.configure(state="disabled")

    def _start_selected(self) -> None:
        game = self.selected_game
        if not game:
            return

        mode = self.config_data.get("console_mode", "vsmile")
        try:
            mame.launch_game(
                mame_path=self.config_data.get("mame_path", ""),
                game_path=str(game.path),
                console_mode=mode,
                bios_path=self.config_data.get("bios_path", ""),
            )
        except mame.LaunchError as exc:
            self._set_status(lambda err=exc: t("status_error", error=err))
        else:
            self._set_status(
                lambda: t("status_started", name=game.label, console=console_label(mode))
            )

    def _set_status(self, text: Callable[[], str]) -> None:
        self._status_text = text
        self._show_status()

    def _show_status(self) -> None:
        self.status_label.configure(text=self._status_text())


def run(version: str) -> None:
    app = LauncherApp(version)
    app.mainloop()

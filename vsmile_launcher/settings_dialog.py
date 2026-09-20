"""Einstellungsdialog fuer die Pfade zu MAME, BIOS, Spielen, V.Flash-Emulator und V.Dream."""

from __future__ import annotations

import sys
from tkinter import filedialog
from typing import Callable

import customtkinter as ctk

from .config import PROJECT_ROOT, resolve_path, to_storable_path
from .i18n import t


class SettingsDialog(ctk.CTkToplevel):
    def __init__(self, master, config: dict, on_save: Callable[[dict], None]):
        super().__init__(master)
        self.title(t("settings_title"))
        self.geometry("580x430")
        self.resizable(False, False)
        self.transient(master)
        self.grab_set()

        self.config_data = config
        self.on_save = on_save

        self.mame_var = ctk.StringVar(value=config.get("mame_path", ""))
        self.bios_var = ctk.StringVar(value=config.get("bios_path", ""))
        self.games_var = ctk.StringVar(value=config.get("games_path", ""))
        self.vflash_var = ctk.StringVar(value=config.get("vflash_path", ""))
        self.vdream_var = ctk.StringVar(value=config.get("vdream_path", ""))

        self._build_row(0, t("settings_mame"), self.mame_var, self._browse_mame)
        self._build_row(1, t("settings_bios"), self.bios_var, self._browse_bios)
        self._build_row(2, t("settings_games"), self.games_var, self._browse_games)
        self._build_row(3, t("settings_vflash"), self.vflash_var, self._browse_vflash)
        self._build_row(4, t("settings_vdream"), self.vdream_var, self._browse_vdream)

        ctk.CTkLabel(
            self, text=t("settings_hint"), text_color="gray60",
            wraplength=520, justify="left", anchor="w",
        ).grid(row=5, column=0, columnspan=3, padx=20, pady=(0, 5), sticky="w")

        button_frame = ctk.CTkFrame(self, fg_color="transparent")
        button_frame.grid(row=6, column=0, columnspan=3, pady=15)

        save_btn = ctk.CTkButton(button_frame, text=t("settings_save"), command=self._save)
        save_btn.pack(side="left", padx=10)

        cancel_btn = ctk.CTkButton(
            button_frame, text=t("settings_cancel"), fg_color="gray40",
            hover_color="gray30", command=self.destroy,
        )
        cancel_btn.pack(side="left", padx=10)

        self.columnconfigure(1, weight=1)

    def _build_row(self, row: int, label: str, var: ctk.StringVar, browse_cmd: Callable) -> None:
        ctk.CTkLabel(self, text=label, width=110, anchor="w").grid(
            row=row, column=0, padx=(20, 5), pady=15, sticky="w"
        )
        entry = ctk.CTkEntry(self, textvariable=var, width=320)
        entry.grid(row=row, column=1, padx=5, pady=15, sticky="ew")
        browse_btn = ctk.CTkButton(self, text=t("settings_browse"), width=100, command=browse_cmd)
        browse_btn.grid(row=row, column=2, padx=(5, 20), pady=15)

    @staticmethod
    def _start_dir(value: str) -> str:
        """Startordner fuer Auswahldialoge: der bisherige Pfad, sonst der Projektordner."""
        if value.strip():
            path = resolve_path(value)
            for candidate in (path, path.parent):
                if candidate.is_dir():
                    return str(candidate)
        return str(PROJECT_ROOT)

    def _browse_mame(self) -> None:
        # Unter Windows heisst die Datei mame.exe, sonst einfach mame.
        pattern = "mame.exe" if sys.platform == "win32" else "mame*"
        path = filedialog.askopenfilename(
            title=t("dialog_select_mame"),
            initialdir=self._start_dir(self.mame_var.get()),
            filetypes=[(t("filetype_mame"), pattern), (t("filetype_all"), "*.*")],
        )
        if path:
            self.mame_var.set(to_storable_path(path))

    def _browse_bios(self) -> None:
        path = filedialog.askdirectory(
            title=t("dialog_select_bios"),
            initialdir=self._start_dir(self.bios_var.get()),
        )
        if path:
            self.bios_var.set(to_storable_path(path))

    def _browse_games(self) -> None:
        path = filedialog.askdirectory(
            title=t("dialog_select_games"),
            initialdir=self._start_dir(self.games_var.get()),
        )
        if path:
            self.games_var.set(to_storable_path(path))

    def _browse_vflash(self) -> None:
        pattern = "vflash.exe" if sys.platform == "win32" else "vflash*"
        path = filedialog.askopenfilename(
            title=t("dialog_select_vflash"),
            initialdir=self._start_dir(self.vflash_var.get()),
            filetypes=[(t("filetype_vflash"), pattern), (t("filetype_all"), "*.*")],
        )
        if path:
            self.vflash_var.set(to_storable_path(path))

    def _browse_vdream(self) -> None:
        pattern = "vdream_core.exe" if sys.platform == "win32" else "vdream_core*"
        path = filedialog.askopenfilename(
            title=t("dialog_select_vdream"),
            initialdir=self._start_dir(self.vdream_var.get()),
            filetypes=[(t("filetype_vdream"), pattern), (t("filetype_all"), "*.*")],
        )
        if path:
            self.vdream_var.set(to_storable_path(path))

    def _save(self) -> None:
        # Auch von Hand eingetippte Pfade werden normalisiert: liegt etwas im
        # Projektordner, wird es relativ gespeichert.
        self.config_data["mame_path"] = to_storable_path(self.mame_var.get())
        self.config_data["bios_path"] = to_storable_path(self.bios_var.get())
        self.config_data["games_path"] = to_storable_path(self.games_var.get())
        self.config_data["vflash_path"] = to_storable_path(self.vflash_var.get())
        self.config_data["vdream_path"] = to_storable_path(self.vdream_var.get())
        self.on_save(self.config_data)
        self.destroy()

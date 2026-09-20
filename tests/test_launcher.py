"""Tests fuer Scanner-Rekursion, portable Pfade und Uebersetzungen.

Ausfuehren im Projektordner:  python -m unittest discover -s tests -v
"""

from __future__ import annotations

import string
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from unittest import mock  # noqa: E402

from vsmile_launcher import config, i18n, mame, vdream, vflash  # noqa: E402
from vsmile_launcher.scanner import (  # noqa: E402
    CD_SYNC,
    SYSTEM_CART,
    SYSTEM_VFLASH,
    scan_games,
)


def touch(path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(b"x")
    return path


def touch_cd(path: Path) -> Path:
    """Legt ein rohes CD-Image an: nur der Sektor-Kopf, der Rest ist egal."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(CD_SYNC + bytes(2340))
    return path


class ScannerTests(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)

    def tearDown(self):
        self._tmp.cleanup()

    def labels(self) -> list[str]:
        return [g.label for g in scan_games(self.root)]

    def test_finds_nested_folders(self):
        touch(self.root / "top.zip")
        touch(self.root / "WiiSmileCard" / "V.Smile Motion" / "DE" / "Spiel (Deutsch).bin")
        self.assertEqual(
            self.labels(),
            ["top.zip", "WiiSmileCard/V.Smile Motion/DE/Spiel (Deutsch).bin"],
        )

    def test_arbitrary_depth(self):
        # 40 Ebenen bleiben unter Windows' Pfadlaengenlimit und gehen trotzdem
        # weit ueber jede feste Tiefe hinaus.
        deep = self.root
        for i in range(40):
            deep = deep / f"d{i}"
        touch(deep / "tief.vsm")
        self.assertEqual(len(scan_games(self.root)), 1)

    def test_same_name_in_different_folders_is_kept(self):
        touch(self.root / "DE" / "game.bin")
        touch(self.root / "EN" / "game.bin")
        self.assertEqual(self.labels(), ["DE/game.bin", "EN/game.bin"])

    def test_filters_bios_and_unknown_extensions_at_any_depth(self):
        touch(self.root / "sub" / "vsmile.zip")
        touch(self.root / "sub" / "BIOS German.bin")
        touch(self.root / "sub" / "readme.txt")
        touch(self.root / "sub" / "OK.BIN")
        self.assertEqual(self.labels(), ["sub/OK.BIN"])

    def test_returns_absolute_paths(self):
        touch(self.root / "a" / "g.zip")
        (game,) = scan_games(self.root)
        self.assertTrue(game.path.is_absolute())
        self.assertTrue(game.path.is_file())

    def test_missing_or_empty_folder(self):
        self.assertEqual(scan_games(""), [])
        self.assertEqual(scan_games(self.root / "gibt-es-nicht"), [])

    def test_relative_games_path_resolves_from_project_root(self):
        name = "_scanner_test_games"
        folder = config.PROJECT_ROOT / name
        try:
            touch(folder / "x" / "y.zip")
            self.assertEqual([g.label for g in scan_games(name)], ["x/y.zip"])
        finally:
            import shutil
            shutil.rmtree(folder, ignore_errors=True)


class CdImageTests(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)

    def tearDown(self):
        self._tmp.cleanup()

    def systems(self) -> dict[str, str]:
        return {g.label: g.system for g in scan_games(self.root)}

    def test_plain_bin_is_a_cartridge(self):
        touch(self.root / "cart.bin")
        self.assertEqual(self.systems(), {"cart.bin": SYSTEM_CART})

    def test_bare_cd_bin_is_recognised_by_its_sync_header(self):
        # So liegen die grossen Spiele (Spider-Man, Shrek) ohne .cue im Ordner.
        touch_cd(self.root / "Spider-Man.bin")
        touch(self.root / "cart.bin")
        self.assertEqual(
            self.systems(), {"Spider-Man.bin": SYSTEM_VFLASH, "cart.bin": SYSTEM_CART}
        )

    def test_cue_is_listed_and_hides_its_bin(self):
        touch_cd(self.root / "Game" / "Game.bin")
        (self.root / "Game" / "Game.cue").write_text(
            'FILE "Game.bin" BINARY\n  TRACK 01 MODE1/2352\n    INDEX 01 00:00:00\n',
            encoding="utf-8",
        )
        self.assertEqual(self.systems(), {"Game/Game.cue": SYSTEM_VFLASH})

    def test_cue_hides_bin_with_a_different_name(self):
        touch_cd(self.root / "data.bin")
        (self.root / "Spiel.cue").write_text('FILE "data.bin" BINARY\n', encoding="utf-8")
        self.assertEqual(self.systems(), {"Spiel.cue": SYSTEM_VFLASH})

    def test_cue_only_hides_its_own_folder(self):
        touch_cd(self.root / "A" / "x.bin")
        (self.root / "A" / "x.cue").write_text('FILE "x.bin" BINARY\n', encoding="utf-8")
        touch_cd(self.root / "B" / "x.bin")
        self.assertEqual(
            self.systems(), {"A/x.cue": SYSTEM_VFLASH, "B/x.bin": SYSTEM_VFLASH}
        )

    def test_unreadable_cue_still_hides_same_named_bin(self):
        touch_cd(self.root / "g.bin")
        (self.root / "g.cue").write_bytes(b"\xff\xfe not text \x00")
        self.assertEqual(self.systems(), {"g.cue": SYSTEM_VFLASH})


class VflashLaunchTests(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)
        self.exe = touch(self.root / "emu dir" / "vflash.exe")
        self.game = touch_cd(self.root / "games" / "Spiel (DE).bin")

    def tearDown(self):
        self._tmp.cleanup()
        i18n.set_language("en")

    def test_build_command_uses_absolute_paths(self):
        cmd = vflash.build_command("vflash/vflash.exe", "games/a b (1).cue")
        self.assertEqual(len(cmd), 2)
        for arg in cmd:
            self.assertTrue(Path(arg).is_absolute(), arg)
        self.assertEqual(Path(cmd[1]).name, "a b (1).cue")

    def test_launch_runs_in_emulator_folder(self):
        with mock.patch.object(vflash.subprocess, "Popen") as popen:
            vflash.launch_game(str(self.exe), str(self.game))
        popen.assert_called_once_with(
            [str(self.exe), str(self.game)], cwd=str(self.exe.parent)
        )

    def test_missing_settings_raise_launch_errors(self):
        cases = [
            (("", str(self.game)), "err_vflash_not_set"),
            (("  ", str(self.game)), "err_vflash_not_set"),
            ((str(self.root / "nope.exe"), str(self.game)), "err_vflash_not_found"),
            ((str(self.exe), str(self.root / "nope.bin")), "err_game_not_found"),
            ((str(self.exe), ""), "err_game_not_found"),
        ]
        for args, key in cases:
            with self.subTest(args=args), self.assertRaises(mame.LaunchError) as ctx:
                vflash.launch_game(*args)
            self.assertEqual(ctx.exception.key, key)

    def test_start_failure_is_wrapped(self):
        with mock.patch.object(vflash.subprocess, "Popen", side_effect=OSError("kaputt")):
            with self.assertRaises(mame.LaunchError) as ctx:
                vflash.launch_game(str(self.exe), str(self.game))
        self.assertEqual(ctx.exception.key, "err_vflash_start_failed")
        self.assertIn("kaputt", str(ctx.exception))

    def test_errors_translate_lazily(self):
        i18n.set_language("de")
        error = mame.LaunchError("err_vflash_not_found", path="x")
        self.assertIn("nicht gefunden", str(error))
        i18n.set_language("en")
        self.assertIn("not found", str(error))


class VdreamLaunchTests(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)
        self.core = touch(self.root / "V Dream" / "vdream_core.exe")
        self.game = touch(self.root / "games" / "Spiel (DE).bin")

    def tearDown(self):
        self._tmp.cleanup()
        i18n.set_language("en")

    def error_key(self, *args, **kwargs) -> str:
        with self.assertRaises(mame.LaunchError) as ctx:
            vdream.launch_game(*args, **kwargs)
        return ctx.exception.key

    def test_launch_passes_rom_and_runs_in_core_folder(self):
        with mock.patch.object(vdream.subprocess, "Popen") as popen:
            vdream.launch_game(str(self.core), str(self.game))
        popen.assert_called_once_with(
            [str(self.core), str(self.game)], cwd=str(self.core.parent)
        )

    def test_extension_check_ignores_case(self):
        game = touch(self.root / "GROSS.BIN")
        with mock.patch.object(vdream.subprocess, "Popen") as popen:
            vdream.launch_game(str(self.core), str(game))
        popen.assert_called_once()

    def test_only_bin_files_are_accepted(self):
        for name in ("a.zip", "b.7z", "c.vsm"):
            game = touch(self.root / name)
            with self.subTest(name=name):
                self.assertEqual(self.error_key(str(self.core), str(game)), "err_vdream_bin_only")

    def test_motion_is_refused(self):
        self.assertEqual(
            self.error_key(str(self.core), str(self.game), "vsmotion"), "err_vdream_no_motion"
        )

    def test_missing_files(self):
        self.assertEqual(
            self.error_key(str(self.root / "nope.exe"), str(self.game)), "err_vdream_not_found"
        )
        self.assertEqual(
            self.error_key(str(self.core), str(self.root / "nope.bin")), "err_game_not_found"
        )
        self.assertEqual(self.error_key(str(self.core), ""), "err_game_not_found")

    def test_start_failure_is_wrapped(self):
        with mock.patch.object(vdream.subprocess, "Popen", side_effect=OSError("kaputt")):
            self.assertEqual(
                self.error_key(str(self.core), str(self.game)), "err_vdream_start_failed"
            )

    def test_empty_path_uses_installed_core(self):
        with mock.patch.object(vdream, "find_installed_core", return_value=self.core):
            with mock.patch.object(vdream.subprocess, "Popen") as popen:
                vdream.launch_game("", str(self.game))
        popen.assert_called_once_with(
            [str(self.core), str(self.game)], cwd=str(self.core.parent)
        )

    def test_empty_path_without_installation_is_an_error(self):
        with mock.patch.object(vdream, "find_installed_core", return_value=None):
            self.assertEqual(self.error_key("", str(self.game)), "err_vdream_not_set")

    def test_find_installed_core_picks_the_newest_version(self):
        base = self.root / "FODSOFT" / "V.Dream"
        touch(base / "v1.4.1" / "vdream_core.exe")
        newest = touch(base / "v1.10.0" / "vdream_core.exe")  # 10 > 4, nicht als Text vergleichen
        touch(base / "v2.0.0" / "readme.txt")  # kein Kern darin
        touch(base / "sonstiges" / "vdream_core.exe")  # kein Versionsordner
        with mock.patch.dict(vdream.os.environ, {"LOCALAPPDATA": str(self.root)}):
            self.assertEqual(vdream.find_installed_core(), newest)

    def test_find_installed_core_without_installation(self):
        with mock.patch.dict(vdream.os.environ, {"LOCALAPPDATA": str(self.root / "leer")}):
            self.assertIsNone(vdream.find_installed_core())
        with mock.patch.dict(vdream.os.environ, {"LOCALAPPDATA": ""}):
            self.assertIsNone(vdream.find_installed_core())


class PathTests(unittest.TestCase):
    def test_inside_project_is_stored_relative(self):
        inside = config.PROJECT_ROOT / "mame" / "mame.exe"
        self.assertEqual(config.to_storable_path(inside), "mame/mame.exe")

    def test_outside_project_stays_absolute(self):
        with tempfile.TemporaryDirectory() as tmp:
            stored = config.to_storable_path(tmp)
            self.assertTrue(Path(stored).is_absolute())

    def test_empty_stays_empty(self):
        self.assertEqual(config.to_storable_path("  "), "")

    def test_project_root_itself(self):
        self.assertEqual(config.to_storable_path(config.PROJECT_ROOT), ".")

    def test_typed_relative_path_round_trips(self):
        stored = config.to_storable_path("games/DE")
        self.assertEqual(stored, "games/DE")
        self.assertEqual(config.resolve_path(stored), config.PROJECT_ROOT / "games" / "DE")

    def test_resolve_ignores_working_directory(self):
        import os
        old = os.getcwd()
        with tempfile.TemporaryDirectory() as tmp:
            os.chdir(tmp)
            try:
                self.assertEqual(config.resolve_path("games"), config.PROJECT_ROOT / "games")
            finally:
                os.chdir(old)

    def test_build_command_uses_absolute_paths(self):
        cmd = mame.build_command("mame/mame.exe", "games/a b (1).bin", "vsmotion", "mame/roms")
        self.assertEqual(cmd[1], "vsmilem")
        for arg in (cmd[0], cmd[3], cmd[5]):
            self.assertTrue(Path(arg).is_absolute(), arg)
        self.assertEqual(Path(cmd[5]).name, "a b (1).bin")

    def test_no_hardcoded_drive_paths_in_sources(self):
        # Ein Laufwerksbuchstabe mit Pfad ("C:/..." oder "C:\\...") darf im Code nicht stehen.
        import re
        pattern = re.compile(r"[A-Za-z]:[\\/](?!/)")
        for source in (config.PROJECT_ROOT / "vsmile_launcher").glob("*.py"):
            for number, line in enumerate(source.read_text(encoding="utf-8").splitlines(), 1):
                self.assertIsNone(pattern.search(line), f"{source.name}:{number}: {line}")


class I18nTests(unittest.TestCase):
    def tearDown(self):
        i18n.set_language("en")

    def test_all_languages_have_identical_keys(self):
        keys = {code: set(table) for code, table in i18n.TRANSLATIONS.items()}
        self.assertEqual(set(keys), set(i18n.LANGUAGES))
        reference = keys["en"]
        for code, table in keys.items():
            self.assertEqual(table, reference, f"Schluessel unterscheiden sich in '{code}'")

    def test_placeholders_match_between_languages(self):
        formatter = string.Formatter()

        def fields(text: str) -> set[str]:
            return {name for _, name, _, _ in formatter.parse(text) if name}

        for key in i18n.TRANSLATIONS["en"]:
            self.assertEqual(
                fields(i18n.TRANSLATIONS["de"][key]),
                fields(i18n.TRANSLATIONS["en"][key]),
                key,
            )

    def test_switching_language(self):
        i18n.set_language("de")
        self.assertEqual(i18n.t("btn_start"), "Starten")
        i18n.set_language("en")
        self.assertEqual(i18n.t("btn_start"), "Start")

    def test_unknown_language_falls_back_to_a_supported_one(self):
        self.assertIn(i18n.set_language("xx"), i18n.LANGUAGES)
        self.assertIn(i18n.set_language(None), i18n.LANGUAGES)

    def test_missing_key_returns_key(self):
        self.assertEqual(i18n.t("gibt_es_nicht"), "gibt_es_nicht")

    def test_launch_error_translates_lazily(self):
        i18n.set_language("de")
        error = mame.LaunchError("err_mame_not_found", path="x")
        self.assertIn("nicht gefunden", str(error))
        i18n.set_language("en")
        self.assertIn("not found", str(error))

    def test_gui_only_uses_existing_keys(self):
        import re
        used = set()
        for source in (config.PROJECT_ROOT / "vsmile_launcher").glob("*.py"):
            if source.name == "i18n.py":
                continue
            text = source.read_text(encoding="utf-8")
            used |= set(re.findall(r'\bt\(\s*f?"([a-z_]+)"', text))
            used |= set(re.findall(r'LaunchError\(\s*"([a-z_]+)"', text))
        used |= {f"console_{m}" for m in ("vsmile", "vsmotion", "vflash")}  # dynamisch gebaut
        used |= {f"emulator_{e}" for e in ("mame", "vdream")}
        self.assertFalse(used - set(i18n.TRANSLATIONS["en"]), used - set(i18n.TRANSLATIONS["en"]))


if __name__ == "__main__":
    unittest.main()

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

from vsmile_launcher import config, i18n, mame  # noqa: E402
from vsmile_launcher.scanner import scan_games  # noqa: E402


def touch(path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(b"x")
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
        used |= {f"console_{m}" for m in ("vsmile", "vsmotion")}  # dynamisch gebaut
        self.assertFalse(used - set(i18n.TRANSLATIONS["en"]), used - set(i18n.TRANSLATIONS["en"]))


if __name__ == "__main__":
    unittest.main()

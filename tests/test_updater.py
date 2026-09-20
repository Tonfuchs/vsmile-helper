"""Tests fuer die Update-Pruefung (ohne Netzwerkzugriff).

Ausfuehren im Projektordner:  python -m unittest discover -s tests -v
"""

from __future__ import annotations

import http.client
import sys
import time
import unittest
import urllib.error
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from vsmile_launcher import updater  # noqa: E402


def release(tag: str = "v1.1.0", url: str | None = None) -> dict:
    return {
        "tag_name": tag,
        "html_url": url or f"https://github.com/{updater.GITHUB_OWNER}/{updater.GITHUB_REPO}/releases/tag/{tag}",
    }


def failing(exc: Exception):
    def fetch():
        raise exc
    return fetch


class VersionTests(unittest.TestCase):
    def test_parse(self):
        self.assertEqual(updater.parse_version("v1.2.3"), (1, 2, 3))
        self.assertEqual(updater.parse_version("1.2"), (1, 2))
        self.assertEqual(updater.parse_version(" V2.0.0-beta.1"), (2, 0, 0))

    def test_parse_rejects_non_versions(self):
        for text in ("", "latest", "release-1.0", "v"):
            self.assertIsNone(updater.parse_version(text), text)

    def test_is_newer(self):
        self.assertTrue(updater.is_newer((1, 0, 1), (1, 0, 0)))
        self.assertTrue(updater.is_newer((1, 10, 0), (1, 9, 0)))  # numerisch, nicht als Text
        self.assertTrue(updater.is_newer((1, 0, 0, 1), (1, 0)))
        self.assertFalse(updater.is_newer((1, 0, 0), (1, 0, 0)))
        self.assertFalse(updater.is_newer((1, 0), (1, 0, 0)))
        self.assertFalse(updater.is_newer((0, 9, 9), (1, 0, 0)))


class CheckForUpdateTests(unittest.TestCase):
    def test_newer_release_is_reported(self):
        info = updater.check_for_update("1.0.0", lambda: release("v1.1.0"))
        self.assertEqual(info.version, "1.1.0")
        self.assertTrue(info.url.endswith("/releases/tag/v1.1.0"))

    def test_same_or_older_release_is_ignored(self):
        self.assertIsNone(updater.check_for_update("1.0.0", lambda: release("v1.0.0")))
        self.assertIsNone(updater.check_for_update("1.0.0", lambda: release("v0.9.0")))

    def test_network_errors_mean_no_update(self):
        for exc in (
            urllib.error.URLError("offline"),
            urllib.error.HTTPError(updater.LATEST_RELEASE_API, 404, "Not Found", {}, None),
            TimeoutError(),
            http.client.IncompleteRead(b""),
            ValueError("kaputtes JSON"),
        ):
            self.assertIsNone(updater.check_for_update("1.0.0", failing(exc)), repr(exc))

    def test_malformed_responses_mean_no_update(self):
        for payload in ([], {}, {"tag_name": 5}, {"tag_name": "nightly"}):
            self.assertIsNone(updater.check_for_update("1.0.0", lambda p=payload: p), repr(payload))

    def test_unparseable_local_version_skips_the_request(self):
        def fetch():
            raise AssertionError("darf nicht aufgerufen werden")
        self.assertIsNone(updater.check_for_update("dev", fetch))

    def test_foreign_release_url_falls_back_to_releases_page(self):
        info = updater.check_for_update("1.0.0", lambda: release("v2.0.0", "https://evil.example/x"))
        self.assertEqual(info.url, updater.RELEASES_PAGE)
        info = updater.check_for_update("1.0.0", lambda: {"tag_name": "v2.0.0"})
        self.assertEqual(info.url, updater.RELEASES_PAGE)

    def test_api_url_points_at_this_repo(self):
        self.assertEqual(
            updater.LATEST_RELEASE_API,
            "https://api.github.com/repos/Tonfuchs/vsmile-helper/releases/latest",
        )


class UpdateCheckThreadTests(unittest.TestCase):
    def wait(self, check: updater.UpdateCheck) -> None:
        deadline = time.monotonic() + 5
        while not check.finished and time.monotonic() < deadline:
            time.sleep(0.01)
        self.assertTrue(check.finished)

    def test_result_arrives_in_background(self):
        check = updater.UpdateCheck("1.0.0", lambda: release("v1.2.0"))
        self.wait(check)
        self.assertEqual(check.result.version, "1.2.0")

    def test_finished_is_set_even_when_the_fetch_crashes(self):
        # Ein unerwarteter Fehler darf die GUI nicht ewig auf das Ergebnis warten lassen.
        check = updater.UpdateCheck("1.0.0", failing(RuntimeError("bug")))
        self.wait(check)
        self.assertIsNone(check.result)


if __name__ == "__main__":
    unittest.main()

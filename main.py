"""Einstiegspunkt fuer den VSmile-MAME-Launcher."""

from vsmile_launcher.app import run

# Muss zum Tag des GitHub-Releases passen ("v1.0.0"); der Updater vergleicht damit.
__version__ = "1.1.0"

if __name__ == "__main__":
    run(__version__)

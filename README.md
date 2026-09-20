# VSmile-MAME-Launcher

Ein schlanker grafischer Launcher fuer V.Smile- und V.Smile-Motion-Spiele unter MAME.

*A lightweight graphical launcher for V.Smile and V.Smile Motion games running under MAME.*

**Sprache / Language:** [Deutsch](#deutsch) · [English](#english)

---

## Deutsch

### Funktionen

- Modernes GUI auf Basis von [customtkinter](https://github.com/TomSchimansky/CustomTkinter)
- **Zwei Sprachen:** Deutsch und English, umschaltbar per Dropdown unten rechts im Hauptfenster. Die Wahl wird in `config.json` gespeichert; beim ersten Start wird die Systemsprache verwendet.
- **Portabel:** Liegen MAME, BIOS oder Spiele im Projektordner, werden ihre Pfade relativ gespeichert. Der ganze Ordner lässt sich verschieben oder auf einen anderen Rechner kopieren.
- **Rekursiver Scan:** Der Spiele-Ordner wird samt aller Unterordner in beliebiger Tiefe durchsucht, z. B. `WiiSmileCard/V.Smile Motion/DE/`. In der Liste steht der Pfad relativ zum Spiele-Ordner, gleichnamige Dateien aus verschiedenen Ordnern lassen sich so unterscheiden.
- Erkannte Endungen: `.zip`, `.bin`, `.iso`, `.vsm`, `.rom`, `.raw` (Gross-/Kleinschreibung egal). BIOS-Archive wie `vsmile.zip` werden ausgeblendet.
- Start eines Spiels per Klick — MAME wird ueber `subprocess` gestartet
- Umschalten zwischen Standard-V.Smile und V.Smile Motion per Dropdown
- **Update-Hinweis:** Beim Start fragt der Launcher im Hintergrund das neueste [GitHub-Release](https://github.com/Tonfuchs/vsmile-helper/releases/latest) ab. Ist dessen Tag neuer als `__version__` in `main.py`, erscheint unten eine dezente Zeile mit dem Button **Herunterladen**, der die Release-Seite im Browser oeffnet. Ohne Internet oder ohne Release passiert nichts.

### Voraussetzungen

- Python 3.10 oder neuer
- Eine funktionierende MAME-Installation (`mame.exe`) mit den V.Smile-Treibern
- Die passenden BIOS-/System-ROMs fuer MAME. **Wichtig:** `vsmile` und `vsmilem` (V.Smile Motion) benoetigen jeweils ein eigenes BIOS-Romset (`vsmile.zip` bzw. `vsmilem.zip` mit der Datei `vsmilemotion.bin`). Fehlt eines davon im BIOS-Ordner, bricht MAME mit `Required files are missing` ab.

Weder MAME noch BIOS oder Spiele gehoeren zu diesem Projekt und muessen selbst besorgt werden.

### Installation

```bash
git clone <repo-url>
cd vsmile-mame-launcher
python -m venv venv
venv\Scripts\activate        # Windows
pip install -r requirements.txt
```

### Nutzung

```bash
python main.py
```

Beim ersten Start ueber **Einstellungen** die folgenden Pfade festlegen:

| Feld | Beschreibung |
| --- | --- |
| `mame.exe` | Pfad zur MAME-Ausfuehrungsdatei |
| BIOS-Ordner | Ordner mit den System-ROMs (wird MAME als zusaetzlicher `-rompath` uebergeben) |
| Spiele-Ordner | Ordner mit den Spiel-Dateien, Unterordner werden automatisch mitgescannt |

Anschliessend erscheinen alle gefundenen Spiele in der Liste. Ein Spiel anklicken, den gewuenschten Konsolen-Modus (V.Smile oder V.Smile Motion) im Dropdown waehlen und auf **Starten** klicken. Nach dem Hinzufuegen neuer Dateien genuegt ein Klick auf **Aktualisieren**.

### Portable Pfade

Der Launcher enthaelt keine festen Pfade. Alle drei Pfade stellt man im Einstellungsdialog ein; beim Speichern gilt:

- Liegt der Pfad **im Projektordner**, wird er relativ gespeichert (z. B. `mame/mame.exe`, `games`) und beim Start vom Projektordner aus aufgeloest, unabhaengig vom aktuellen Arbeitsverzeichnis.
- Liegt er **ausserhalb** (anderes Laufwerk, `Downloads`, ...), bleibt er ein absoluter Pfad.

Eine voll portable Installation sieht so aus:

```text
vsmile-mame-launcher/
├── main.py
├── config.json          # "mame_path": "mame/mame.exe", "games_path": "games", ...
├── mame/                # MAME samt roms/ mit den BIOS-Dateien
└── games/               # beliebig tief verschachtelt
```

`mame/`, `games/` und `roms/` stehen in der `.gitignore`, damit versehentlich keine ROMs ins Repository gelangen.

### Aufgerufene MAME-Kommandos

Der Launcher ruft MAME je nach gewaehltem Modus wie folgt auf (alle Pfade absolut):

```bash
mame.exe vsmile -cart "<Pfad_zum_Spiel>"
mame.exe vsmilem -cart "<Pfad_zum_Spiel>"
```

Ist ein BIOS-Ordner hinterlegt, wird zusaetzlich `-rompath "<BIOS-Ordner>"` angehaengt, damit MAME die System-ROMs findet.

### Konfigurationsdatei

Die Datei `config.json` wird automatisch im Projektordner angelegt und ist Teil der `.gitignore`, da sie lokale, geraeteabhaengige Pfade enthaelt. Ein Beispiel liegt unter `config.example.json`.

| Schluessel | Bedeutung |
| --- | --- |
| `mame_path`, `bios_path`, `games_path` | Pfade, relativ zum Projektordner oder absolut |
| `console_mode` | `vsmile` oder `vsmotion` |
| `language` | `de` oder `en`; leer = Systemsprache |

### Tests

```bash
python -m unittest discover -s tests -v
```

### Release veroeffentlichen

Auf GitHub unter **Actions → Release → Run workflow** (Branch `main`) die neue Versionsnummer im Format `X.Y.Z` eintragen, z. B. `1.1.0`. Der Workflow prueft, dass sie groesser als die aktuelle ist, setzt `__version__` in `main.py`, fuehrt die Tests aus, committet auf `main`, legt den Tag `v1.1.0` an und veroeffentlicht ein Release mit Quellcode-ZIP. Ab dann zeigt der Update-Hinweis in aelteren Launcher-Versionen die neue Fassung an.

### Projektstruktur

```text
vsmile-mame-launcher/
├── main.py                     # Einstiegspunkt
├── .github/
│   ├── workflows/release.yml   # Release-Workflow (manuell, mit Versionsnummer)
│   └── scripts/set_version.py  # setzt __version__ in main.py
├── vsmile_launcher/
│   ├── app.py                  # Hauptfenster / GUI
│   ├── settings_dialog.py      # Einstellungsdialog
│   ├── config.py               # config.json, relative/absolute Pfade
│   ├── i18n.py                 # Uebersetzungen (de/en)
│   ├── scanner.py              # Rekursives Scannen des Spiele-Ordners
│   ├── updater.py              # Update-Pruefung ueber die GitHub-API
│   └── mame.py                 # MAME-Kommandoaufbau und -start
├── tests/
├── config.example.json
├── requirements.txt
└── .gitignore
```

### Weitere Sprache hinzufuegen

In `vsmile_launcher/i18n.py` einen Eintrag in `LANGUAGES` und eine Tabelle in `TRANSLATIONS` mit denselben Schluesseln wie `en` anlegen. Die Tests pruefen, dass kein Schluessel fehlt.

---

## English

### Features

- Modern GUI built with [customtkinter](https://github.com/TomSchimansky/CustomTkinter)
- **Two languages:** German and English, switchable via the dropdown at the bottom right of the main window. The choice is saved in `config.json`; on first launch the system language is used.
- **Portable:** if MAME, the BIOS or the games live inside the project folder, their paths are stored relative to it. You can move the whole folder or copy it to another machine.
- **Recursive scan:** the games folder is searched including all subfolders at any depth, e.g. `WiiSmileCard/V.Smile Motion/DE/`. The list shows each path relative to the games folder, so files with the same name in different folders stay distinguishable.
- Recognised extensions: `.zip`, `.bin`, `.iso`, `.vsm`, `.rom`, `.raw` (case-insensitive). BIOS archives such as `vsmile.zip` are hidden.
- Launch a game with a single click — MAME is started via `subprocess`
- Switch between standard V.Smile and V.Smile Motion via a dropdown
- **Update notice:** on startup the launcher checks the latest [GitHub release](https://github.com/Tonfuchs/vsmile-helper/releases/latest) in the background. If its tag is newer than `__version__` in `main.py`, a subtle line with a **Download** button appears at the bottom and opens the release page in your browser. Offline or without a release, nothing happens.

### Requirements

- Python 3.10 or newer
- A working MAME installation (`mame.exe`) with the V.Smile drivers
- The matching BIOS/system ROMs for MAME. **Important:** `vsmile` and `vsmilem` (V.Smile Motion) each need their own BIOS romset (`vsmile.zip` and `vsmilem.zip` containing `vsmilemotion.bin`). Missing either one makes MAME abort with `Required files are missing`.

Neither MAME nor BIOS files or games are part of this project; you have to obtain them yourself.

### Installation

```bash
git clone <repo-url>
cd vsmile-mame-launcher
python -m venv venv
venv\Scripts\activate        # Windows
pip install -r requirements.txt
```

### Usage

```bash
python main.py
```

On first launch, open **Settings** and configure the following paths:

| Field | Description |
| --- | --- |
| `mame.exe` | Path to the MAME executable |
| BIOS folder | Folder containing the system ROMs (passed to MAME as an additional `-rompath`) |
| Games folder | Folder containing the game files; subfolders are scanned automatically |

All detected games then appear in the list. Click a game, pick the desired console mode (V.Smile or V.Smile Motion) from the dropdown, and click **Start**. After adding new files, click **Refresh**.

### Portable paths

The launcher contains no hardcoded paths. You set all three paths in the settings dialog; when saving:

- A path **inside the project folder** is stored relative (e.g. `mame/mame.exe`, `games`) and resolved against the project folder at launch, regardless of the current working directory.
- A path **outside** it (another drive, `Downloads`, ...) stays absolute.

A fully portable setup looks like this:

```text
vsmile-mame-launcher/
├── main.py
├── config.json          # "mame_path": "mame/mame.exe", "games_path": "games", ...
├── mame/                # MAME including roms/ with the BIOS files
└── games/               # nested as deeply as you like
```

`mame/`, `games/` and `roms/` are listed in `.gitignore` so ROMs never end up in the repository by accident.

### MAME commands invoked

Depending on the selected mode, the launcher runs (all paths absolute):

```bash
mame.exe vsmile -cart "<path_to_game>"
mame.exe vsmilem -cart "<path_to_game>"
```

If a BIOS folder is configured, `-rompath "<bios_folder>"` is appended so MAME can locate the system ROMs.

### Configuration file

`config.json` is created automatically in the project folder and is excluded via `.gitignore`, since it contains local, machine-specific paths. An example file is provided as `config.example.json`.

| Key | Meaning |
| --- | --- |
| `mame_path`, `bios_path`, `games_path` | Paths, relative to the project folder or absolute |
| `console_mode` | `vsmile` or `vsmotion` |
| `language` | `de` or `en`; empty = system language |

### Tests

```bash
python -m unittest discover -s tests -v
```

### Publishing a release

On GitHub open **Actions → Release → Run workflow** (branch `main`) and enter the new version as `X.Y.Z`, e.g. `1.1.0`. The workflow checks that it is greater than the current one, sets `__version__` in `main.py`, runs the tests, commits to `main`, creates the tag `v1.1.0` and publishes a release with a source ZIP. From then on the update notice in older launcher versions points to the new release.

### Project structure

```text
vsmile-mame-launcher/
├── main.py                     # Entry point
├── .github/
│   ├── workflows/release.yml   # Release workflow (manual, takes a version number)
│   └── scripts/set_version.py  # sets __version__ in main.py
├── vsmile_launcher/
│   ├── app.py                  # Main window / GUI
│   ├── settings_dialog.py      # Settings dialog
│   ├── config.py               # config.json, relative/absolute paths
│   ├── i18n.py                 # Translations (de/en)
│   ├── scanner.py              # Recursive games folder scanning
│   ├── updater.py              # Update check via the GitHub API
│   └── mame.py                 # MAME command building and launching
├── tests/
├── config.example.json
├── requirements.txt
└── .gitignore
```

### Adding another language

Add an entry to `LANGUAGES` and a table to `TRANSLATIONS` in `vsmile_launcher/i18n.py`, with the same keys as `en`. The tests verify that no key is missing.

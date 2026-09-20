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
- Erkannte Endungen: `.zip`, `.bin`, `.iso`, `.vsm`, `.rom`, `.raw`, `.cue` (Gross-/Kleinschreibung egal). BIOS-Archive wie `vsmile.zip` werden ausgeblendet.
- Start eines Spiels per Klick — MAME wird ueber `subprocess` gestartet
- Umschalten zwischen Standard-V.Smile und V.Smile Motion per Dropdown
- **Zweiter Emulator fuer Cartridges:** Per Dropdown **Emulator** zwischen MAME und [V.Dream](#v.dream-als-alternative-fuer-cartridges) umschalten.
- **V.Flash-CDs (experimentell):** CD-Images (`.cue` oder rohe `.bin`) werden erkannt, mit `[V.Flash]` markiert und an einen externen V.Flash-Emulator uebergeben, siehe [V.Flash-CDs](#v.flash-cds-experimentell).
- **Update-Hinweis:** Beim Start fragt der Launcher im Hintergrund das neueste [GitHub-Release](https://github.com/Tonfuchs/vsmile-helper/releases/latest) ab. Ist dessen Tag neuer als `__version__` in `main.py`, erscheint unten eine dezente Zeile mit dem Button **Herunterladen**, der die Release-Seite im Browser oeffnet. Ohne Internet oder ohne Release passiert nichts.

### Voraussetzungen

- Python 3.10 oder neuer
- Eine funktionierende MAME-Installation (`mame.exe`) mit den V.Smile-Treibern
- Die passenden BIOS-/System-ROMs fuer MAME. **Wichtig:** `vsmile` und `vsmilem` (V.Smile Motion) benoetigen jeweils ein eigenes BIOS-Romset (`vsmile.zip` bzw. `vsmilem.zip` mit der Datei `vsmilemotion.bin`). Fehlt eines davon im BIOS-Ordner, bricht MAME mit `Required files are missing` ab.

- Optional, nur fuer V.Flash-CDs: ein V.Flash-Emulator (`vflash.exe`), siehe [V.Flash-CDs](#v.flash-cds-experimentell)
- Optional: [V.Dream](https://github.com/fodsoft/vdream) als zweiter Emulator fuer V.Smile-Cartridges

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
| `vflash.exe` | Optional: V.Flash-Emulator fuer CD-Spiele |
| `vdream_core.exe` | Optional: Kern von V.Dream. Leer = die installierte Fassung suchen |

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

### V.Dream als Alternative fuer Cartridges

Im Dropdown **Emulator** laesst sich fuer Cartridges statt MAME [V.Dream](https://github.com/fodsoft/vdream) waehlen. Der Launcher startet dann den Kern der Installation (Arbeitsverzeichnis ist dessen Ordner, dort liegen die Speicherstaende):

```bash
vdream_core.exe "<Pfad_zum_Spiel.bin>"
```

Ein BIOS ist dafuer nicht noetig. Ist unter **Einstellungen → vdream_core.exe** nichts eingetragen, sucht der Launcher die neueste Fassung im Standardordner des Installers (`%LOCALAPPDATA%\FODSOFT\V.Dream\vX.Y.Z\`).

Grenzen, die getestet wurden (V.Dream 1.4.1): Der Kern startet nur rohe `.bin`-Dateien, keine `.zip`/`.7z`, und zeigt V.Smile-Motion-Spiele nur als Bildrauschen. Der Launcher meldet beides vorab und verweist auf MAME. V.Flash-CDs kann diese Fassung nicht. Ein Spiel, das in MAME und V.Dream laeuft, laesst sich so direkt vergleichen; welcher Emulator besser laeuft, ist nicht untersucht.

### V.Flash-CDs (experimentell)

Sehr grosse Images (mehrere hundert MB, z. B. *Spider-Man – Angriff der Super-Schurken* oder *Shrek der Dritte*) sind keine V.Smile-Cartridges, sondern CDs der **V.Flash** (in Europa **V.Smile Pro**). Das ist eine andere Konsole, MAME hat dafuer keinen Treiber und startet sie nicht.

Der Launcher erkennt solche Spiele an einer `.cue`-Datei oder am CD-Sektorkopf einer rohen `.bin`, kennzeichnet sie in der Liste mit `[V.Flash]` und ruft statt MAME einen externen Emulator auf (Arbeitsverzeichnis ist der Ordner der `vflash.exe`):

```bash
vflash.exe "<Pfad_zum_Image>"
```

- Ein Emulator gehoert nicht zu diesem Projekt. Bekannt ist [vflash-emu](https://github.com/WizzardSK/vflash-emu), ein sehr frueher Ansatz. Nach dessen eigener README ist er Linux-Quellcode (SDL2, libjpeg), bringt keine fertige Windows-Fassung mit und startet noch keine spielbaren Spiele (Bildergalerie und Videos von der CD sowie ein Boot-Versuch). Man muss ihn selbst bauen oder portieren und den Pfad zur Programmdatei unter **Einstellungen → vflash.exe** eintragen.
- Die Boot-ROM `70004.bin` gehoert in den Ordner der `vflash.exe` oder nach `../vflash-roms/`.
- Ohne eingestellten Pfad zeigt der Launcher beim Start einer V.Flash-CD eine Fehlermeldung. Alle anderen Spiele laufen unveraendert ueber MAME.
- Liegt zu einer `.bin` eine `.cue`, erscheint nur die `.cue`. Der Ordner `vflash/` steht in der `.gitignore`, falls man den Emulator im Projektordner ablegt.

### Konfigurationsdatei

Die Datei `config.json` wird automatisch im Projektordner angelegt und ist Teil der `.gitignore`, da sie lokale, geraeteabhaengige Pfade enthaelt. Ein Beispiel liegt unter `config.example.json`.

| Schluessel | Bedeutung |
| --- | --- |
| `mame_path`, `bios_path`, `games_path` | Pfade, relativ zum Projektordner oder absolut |
| `vflash_path` | Optional: Pfad zum V.Flash-Emulator, relativ oder absolut |
| `cart_emulator` | `mame` oder `vdream`: Emulator fuer Cartridges |
| `vdream_path` | Optional: Pfad zu `vdream_core.exe`; leer = installierte Fassung suchen |
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
│   ├── mame.py                 # MAME-Kommandoaufbau und -start
│   ├── vdream.py               # Start des V.Dream-Kerns fuer Cartridges
│   └── vflash.py               # Start des externen V.Flash-Emulators
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
- Recognised extensions: `.zip`, `.bin`, `.iso`, `.vsm`, `.rom`, `.raw`, `.cue` (case-insensitive). BIOS archives such as `vsmile.zip` are hidden.
- Launch a game with a single click — MAME is started via `subprocess`
- Switch between standard V.Smile and V.Smile Motion via a dropdown
- **Second emulator for cartridges:** switch between MAME and [V.Dream](#v.dream-as-an-alternative-for-cartridges) with the **Emulator** dropdown.
- **V.Flash CDs (experimental):** CD images (`.cue` or raw `.bin`) are detected, tagged `[V.Flash]` and handed to an external V.Flash emulator, see [V.Flash CDs](#v.flash-cds-experimental).
- **Update notice:** on startup the launcher checks the latest [GitHub release](https://github.com/Tonfuchs/vsmile-helper/releases/latest) in the background. If its tag is newer than `__version__` in `main.py`, a subtle line with a **Download** button appears at the bottom and opens the release page in your browser. Offline or without a release, nothing happens.

### Requirements

- Python 3.10 or newer
- A working MAME installation (`mame.exe`) with the V.Smile drivers
- The matching BIOS/system ROMs for MAME. **Important:** `vsmile` and `vsmilem` (V.Smile Motion) each need their own BIOS romset (`vsmile.zip` and `vsmilem.zip` containing `vsmilemotion.bin`). Missing either one makes MAME abort with `Required files are missing`.

- Optional, only for V.Flash CDs: a V.Flash emulator (`vflash.exe`), see [V.Flash CDs](#v.flash-cds-experimental)
- Optional: [V.Dream](https://github.com/fodsoft/vdream) as a second emulator for V.Smile cartridges

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
| `vflash.exe` | Optional: V.Flash emulator for CD games |
| `vdream_core.exe` | Optional: V.Dream core. Empty = look for the installed version |

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

### V.Dream as an alternative for cartridges

The **Emulator** dropdown lets you pick [V.Dream](https://github.com/fodsoft/vdream) instead of MAME for cartridges. The launcher then starts the core of the installation (its working directory is the install folder, where the saves live):

```bash
vdream_core.exe "<path_to_game.bin>"
```

No BIOS is needed. If **Settings → vdream_core.exe** is empty, the launcher looks for the newest version in the installer's default folder (`%LOCALAPPDATA%\FODSOFT\V.Dream\vX.Y.Z\`).

Limits that were tested (V.Dream 1.4.1): the core only runs raw `.bin` files, not `.zip`/`.7z`, and shows V.Smile Motion games as pure noise. The launcher reports both up front and points to MAME. This version cannot run V.Flash CDs. A game that runs in both MAME and V.Dream can be compared directly; which emulator performs better has not been investigated.

### V.Flash CDs (experimental)

Very large images (several hundred MB, e.g. *Spider-Man – Attack of the Super Villains* or *Shrek the Third*) are not V.Smile cartridges but CDs for the **V.Flash** (called **V.Smile Pro** in Europe). That is a different console; MAME has no driver for it and cannot run them.

The launcher detects these games by a `.cue` file or by the CD sector header of a raw `.bin`, tags them `[V.Flash]` in the list and calls an external emulator instead of MAME (the working directory is the folder of `vflash.exe`):

```bash
vflash.exe "<path_to_image>"
```

- No emulator is part of this project. One known option is [vflash-emu](https://github.com/WizzardSK/vflash-emu), a very early effort. According to its own README it is Linux source code (SDL2, libjpeg), ships no ready-made Windows build and does not run playable games yet (image gallery and videos from the disc plus a boot attempt). You have to build or port it yourself and enter the path to the executable under **Settings → vflash.exe**.
- The boot ROM `70004.bin` belongs next to `vflash.exe` or in `../vflash-roms/`.
- Without a configured path the launcher shows an error when you start a V.Flash CD. All other games keep running through MAME.
- If a `.bin` has a matching `.cue`, only the `.cue` is listed. The `vflash/` folder is in `.gitignore` in case you keep the emulator inside the project folder.

### Configuration file

`config.json` is created automatically in the project folder and is excluded via `.gitignore`, since it contains local, machine-specific paths. An example file is provided as `config.example.json`.

| Key | Meaning |
| --- | --- |
| `mame_path`, `bios_path`, `games_path` | Paths, relative to the project folder or absolute |
| `vflash_path` | Optional: path to the V.Flash emulator, relative or absolute |
| `cart_emulator` | `mame` or `vdream`: emulator used for cartridges |
| `vdream_path` | Optional: path to `vdream_core.exe`; empty = look for the installed version |
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
│   ├── mame.py                 # MAME command building and launching
│   ├── vdream.py               # Launching the V.Dream core for cartridges
│   └── vflash.py               # Launching the external V.Flash emulator
├── tests/
├── config.example.json
├── requirements.txt
└── .gitignore
```

### Adding another language

Add an entry to `LANGUAGES` and a table to `TRANSLATIONS` in `vsmile_launcher/i18n.py`, with the same keys as `en`. The tests verify that no key is missing.

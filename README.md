# Create Shortcut — Dolphin Service Menu

[**Русская версия**](README_ru.md)

Adds **"Create Shortcut"** and **"Edit Shortcut"** entries to the Dolphin right-click context menu. Creates `.desktop` shortcut files — the Linux equivalent of Windows `.lnk` files.

## Features

- **Create Shortcut** — right-click any file/folder → creates a `.desktop` shortcut next to it
- **Edit Shortcut** — right-click an existing `.desktop` shortcut → change Wine/Proton runner
- **.exe support** — creates `Type=Application` shortcuts (works via Wine or Proton)
- **Icon extraction** — automatically extracts and caches icons from `.exe` files (requires `icoutils`)
- **Proton support** — detects installed Proton versions (GE-Proton, Steam Proton, etc.) and allows selecting one
- **GUI dialog** — native Plasma 6 styled dialog with icon preview and runner selector
- **Auto-language** — menu and dialog in English / Русский / Українська (auto-detected from system locale)

## Requirements

| Package | Purpose |
|---------|---------|
| `kio` | Dolphin service menu support (usually pre-installed) |
| `icoutils` | Extract icons from `.exe` files |
| `pyside6` | GUI dialog for .exe runner selection |

Install dependencies:

```bash
sudo pacman -S icoutils pyside6
```

## Installation

### Quick install (user only)

```bash
git clone https://github.com/yourusername/Plasma-Shortcut
cd Plasma-Shortcut
./install.sh
```

### System-wide

```bash
sudo ./install.sh
```

### Arch Linux (PKGBUILD)

```bash
makepkg -si
```

### Uninstall

```bash
# user install
./uninstall.sh

# system-wide
sudo ./uninstall.sh
```

## Screenshots

<p align="center">
  <img src="1.png" alt="Create Shortcut dialog" width="45%">
  <img src="2.png" alt="Context menu" width="45%">
</p>

## Usage

### Create a shortcut

Right-click any file or folder in Dolphin → **Create Shortcut** → **Create .desktop Shortcut**

For `.exe` files, a GUI dialog opens with:
- Icon preview (extracted from the .exe)
- Runner selector: **Wine** (default) or any installed **Proton** version
- Click **Create** → `.desktop` file appears in the same directory

Drag the `.desktop` file to your desktop or panel to pin it.

### Edit a shortcut

Right-click an existing `.desktop` shortcut → **Edit Shortcut** → change Wine ↔ Proton → **Save**

## Project structure

```
Plasma-Shortcut/
├── install.sh                         # Install script
├── uninstall.sh                       # Uninstall script
├── PKGBUILD                           # Arch Linux package
├── README.md                          # This file
├── README_ru.md                       # Russian readme
├── Plasma-Shortcut.install # Pacman hooks
└── src/
    ├── dolphin-create-shortcut        # Bash script (create mode)
    ├── dolphin-edit-shortcut          # Bash script (edit mode)
    ├── dolphin-shortcut-dialog.py     # Python GUI dialog
    ├── create-shortcut.desktop        # Service menu (all files)
    └── edit-shortcut.desktop          # Service menu (.desktop files only)
```

## License

GNU GPL v2

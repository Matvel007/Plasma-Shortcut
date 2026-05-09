#!/bin/bash

set -e

PREFIX="${PREFIX:-/usr/local}"
USER_INSTALL="${USER_INSTALL:-false}"

if [ "$USER_INSTALL" = "true" ]; then
    BIN_DIR="$HOME/.local/bin"
    MENU_DIR="$HOME/.local/share/kio/servicemenus"
    PREFIX_HOME="$HOME/.local"
else
    BIN_DIR="$PREFIX/bin"
    MENU_DIR="$PREFIX/share/kio/servicemenus"
    PREFIX_HOME="$PREFIX"
fi

echo "Installing Create Shortcut Service Menu..."
echo "  Bin dir:  $BIN_DIR"
echo "  Menu dir: $MENU_DIR"

if ! command -v wrestool &>/dev/null || ! command -v icotool &>/dev/null; then
    echo "Installing icoutils (required for .exe icon extraction)..."
    if command -v pacman &>/dev/null; then
        if [ "$(id -u)" -eq 0 ]; then
            pacman -S icoutils --noconfirm
        else
            sudo pacman -S icoutils --noconfirm 2>/dev/null || pkexec pacman -S icoutils --noconfirm
        fi
    elif command -v apt &>/dev/null; then
        if [ "$(id -u)" -eq 0 ]; then
            apt install -y icoutils
        else
            sudo apt install -y icoutils
        fi
    elif command -v dnf &>/dev/null; then
        if [ "$(id -u)" -eq 0 ]; then
            dnf install -y icoutils
        else
            sudo dnf install -y icoutils
        fi
    else
        echo "Warning: icoutils not found. Install it manually for .exe icon support."
    fi
fi

if ! python3 -c "from PySide6.QtWidgets import QApplication" 2>/dev/null; then
    echo "Installing pyside6 (required for GUI dialog)..."
    if command -v pacman &>/dev/null; then
        if [ "$(id -u)" -eq 0 ]; then
            pacman -S pyside6 --noconfirm
        else
            sudo pacman -S pyside6 --noconfirm 2>/dev/null || pkexec pacman -S pyside6 --noconfirm
        fi
    fi
fi

mkdir -p "$BIN_DIR" "$MENU_DIR"

cp src/dolphin-create-shortcut "$BIN_DIR/dolphin-create-shortcut"
chmod +x "$BIN_DIR/dolphin-create-shortcut"

cp src/dolphin-edit-shortcut "$BIN_DIR/dolphin-edit-shortcut"
chmod +x "$BIN_DIR/dolphin-edit-shortcut"

cp src/dolphin-launch-mode "$BIN_DIR/dolphin-launch-mode"
chmod +x "$BIN_DIR/dolphin-launch-mode"

cp src/dolphin-extract-icon "$BIN_DIR/dolphin-extract-icon"
chmod +x "$BIN_DIR/dolphin-extract-icon"

SHARE_DIR="${PREFIX}/share/create-shortcut"
if [ "$USER_INSTALL" = "true" ]; then
    SHARE_DIR="$HOME/.local/share/create-shortcut"
fi
mkdir -p "$SHARE_DIR"
cp src/dolphin-shortcut-dialog.py "$SHARE_DIR/dolphin-shortcut-dialog.py"
chmod +x "$SHARE_DIR/dolphin-shortcut-dialog.py"
cp src/dolphin-launch-mode-dialog.py "$SHARE_DIR/dolphin-launch-mode-dialog.py"
chmod +x "$SHARE_DIR/dolphin-launch-mode-dialog.py"

sed "s|PREFIX|$PREFIX_HOME|g" src/create-shortcut.desktop > "$MENU_DIR/create-shortcut.desktop"
chmod +x "$MENU_DIR/create-shortcut.desktop"

sed "s|PREFIX|$PREFIX_HOME|g" src/edit-shortcut.desktop > "$MENU_DIR/edit-shortcut.desktop"
chmod +x "$MENU_DIR/edit-shortcut.desktop"

sed "s|PREFIX|$PREFIX_HOME|g" src/launch-mode.desktop > "$MENU_DIR/launch-mode.desktop"
chmod +x "$MENU_DIR/launch-mode.desktop"

sed "s|PREFIX|$PREFIX_HOME|g" src/extract-icon.desktop > "$MENU_DIR/extract-icon.desktop"
chmod +x "$MENU_DIR/extract-icon.desktop"

if command -v kbuildsycoca6 &>/dev/null; then
    echo "Rebuilding KDE service cache..."
    kbuildsycoca6
elif command -v kbuildsycoca5 &>/dev/null; then
    echo "Rebuilding KDE service cache..."
    kbuildsycoca5
fi

echo "Done! Restart Dolphin or run: kbuildsycoca6"

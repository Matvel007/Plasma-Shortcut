#!/bin/bash

set -e

USER_INSTALL="${USER_INSTALL:-false}"

if [ "$USER_INSTALL" = "true" ]; then
    BIN_DIR="$HOME/.local/bin"
    MENU_DIR="$HOME/.local/share/kio/servicemenus"
else
    BIN_DIR="${PREFIX:-/usr/local}/bin"
    MENU_DIR="${PREFIX:-/usr/local}/share/kio/servicemenus"
fi

echo "Uninstalling Create Shortcut Service Menu..."

rm -f "$BIN_DIR/dolphin-create-shortcut"
rm -f "$MENU_DIR/create-shortcut.desktop"

if command -v kbuildsycoca6 &>/dev/null; then
    kbuildsycoca6
elif command -v kbuildsycoca5 &>/dev/null; then
    kbuildsycoca5
fi

echo "Done."

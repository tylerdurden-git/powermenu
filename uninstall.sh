#!/usr/bin/env bash
set -e

APP_PATH="$HOME/.local/bin/quickmenu.py"
UNINSTALL_PATH="$HOME/.local/bin/quickmenu-uninstall.sh"
SCHEMA="org.gnome.settings-daemon.plugins.media-keys"

echo "==> Removing app files..."
rm -f "$APP_PATH" "$UNINSTALL_PATH"

echo "==> Removing shortcut..."
EXISTING=$(gsettings get $SCHEMA custom-keybindings)

for path in $(echo "$EXISTING" | tr -d "[]'," | tr " " "\n"); do
    NAME=$(gsettings get "$SCHEMA.custom-keybinding:$path" name 2>/dev/null || true)
    if [ "$NAME" = "'Quick Menu'" ]; then
        gsettings reset-recursively "$SCHEMA.custom-keybinding:$path"
        NEW_LIST=$(echo "$EXISTING" | sed "s|'$path', ||; s|, '$path'||; s|'$path'||")
        gsettings set $SCHEMA custom-keybindings "$NEW_LIST"
        break
    fi
done

echo "Quick Menu removed."

#!/usr/bin/env bash
set -e

RAW_BASE="https://raw.githubusercontent.com/tylerdurden-git/powermenu/main"
INSTALL_DIR="$HOME/.local/bin"
APP_PATH="$INSTALL_DIR/quickmenu.py"
UNINSTALL_PATH="$INSTALL_DIR/quickmenu-uninstall.sh"

echo "==> [1/3] Installing dependencies..."
sudo apt update -qq
sudo apt install -y python3-gi gir1.2-gtk-3.0 gnome-system-monitor gnome-terminal wireplumber curl

echo "==> [2/3] Setting up files..."
mkdir -p "$INSTALL_DIR"
curl -sSL "$RAW_BASE/quickmenu.py" -o "$APP_PATH"
chmod +x "$APP_PATH"

curl -sSL "$RAW_BASE/uninstall.sh" -o "$UNINSTALL_PATH"
chmod +x "$UNINSTALL_PATH"

echo "==> [3/3] Binding Super + X shortcut..."
SCHEMA="org.gnome.settings-daemon.plugins.media-keys"
EXISTING=$(gsettings get $SCHEMA custom-keybindings)

SLOT=0
TARGET_PATH=""
while [[ "$EXISTING" == *"custom$SLOT/"* ]]; do
    CHECK_PATH="/org/gnome/settings-daemon/plugins/media-keys/custom-keybindings/custom$SLOT/"
    NAME=$(gsettings get "$SCHEMA.custom-keybinding:$CHECK_PATH" name 2>/dev/null || true)
    if [ "$NAME" = "'Quick Menu'" ]; then
        TARGET_PATH="$CHECK_PATH"
        break
    fi
    ((SLOT++))
done

if [ -z "$TARGET_PATH" ]; then
    TARGET_PATH="/org/gnome/settings-daemon/plugins/media-keys/custom-keybindings/custom$SLOT/"
    if [ "$EXISTING" = "@as []" ] || [ "$EXISTING" = "[]" ]; then
        gsettings set $SCHEMA custom-keybindings "['$TARGET_PATH']"
    else
        UPDATED=$(echo "$EXISTING" | sed "s/]/, '$TARGET_PATH']/")
        gsettings set $SCHEMA custom-keybindings "$UPDATED"
    fi
fi

gsettings set "$SCHEMA.custom-keybinding:$TARGET_PATH" name 'Quick Menu'
gsettings set "$SCHEMA.custom-keybinding:$TARGET_PATH" command "$APP_PATH"
gsettings set "$SCHEMA.custom-keybinding:$TARGET_PATH" binding '<Super>x'

echo ""
echo "Installed successfully! Press Super + X (Win + X) to open."

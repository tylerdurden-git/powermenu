#!/usr/bin/env python3
import sys
import subprocess
import gi
gi.require_version('Gtk', '3.0')
gi.require_version('Gdk', '3.0')
from gi.repository import Gtk, Gdk

def execute_action(action_type):
    Gtk.main_quit()

    commands = {
        "shutdown": "systemctl poweroff",
        "reboot": "systemctl reboot",
        "suspend": "systemctl suspend",
        "lock": "loginctl lock-session",
        "logout": "gnome-session-quit --logout --no-prompt 2>/dev/null || loginctl terminate-session ${XDG_SESSION_ID:-self}",
        "task_manager": "gnome-system-monitor &",
        "terminal": "gnome-terminal &",
        "night_light": """
            STATUS=$(gsettings get org.gnome.settings-daemon.plugins.color night-light-enabled)
            if [ "$STATUS" = "true" ]; then
                gsettings set org.gnome.settings-daemon.plugins.color night-light-enabled false
            else
                gsettings set org.gnome.settings-daemon.plugins.color night-light-enabled true
            fi
        """,
        "mic_mute": "wpctl set-mute @DEFAULT_AUDIO_SOURCE@ toggle",
        "audio_mute": "wpctl set-mute @DEFAULT_AUDIO_SINK@ toggle",
        "dnd": """
            STATUS=$(gsettings get org.gnome.desktop.notifications show-banners)
            if [ "$STATUS" = "true" ]; then
                gsettings set org.gnome.desktop.notifications show-banners false
            else
                gsettings set org.gnome.desktop.notifications show-banners true
            fi
        """
    }

    cmd = commands.get(action_type)
    if cmd:
        subprocess.Popen(cmd, shell=True, executable="/bin/bash")
    sys.exit(0)


class QuickMenu(Gtk.Window):
    def __init__(self):
        super().__init__(type=Gtk.WindowType.TOPLEVEL)
        self.set_title("Quick Menu")
        self.set_decorated(False)
        self.set_resizable(False)
        self.set_default_size(280, 480)
        self.set_position(Gtk.WindowPosition.CENTER)
        self.set_modal(True)
        self.set_keep_above(True)
        self.set_skip_taskbar_hint(True)
        self.set_skip_pager_hint(True)

        css = b"""
        window {
            background-color: #1e1e2e;
            border: 1px solid #45475a;
            border-radius: 14px;
            padding: 10px;
        }
        button {
            background: transparent;
            border: none;
            border-radius: 8px;
            padding: 6px 12px;
            color: #cdd6f4;
            font-size: 13px;
            font-weight: 500;
        }
        button:hover {
            background-color: #313244;
            color: #89b4fa;
        }
        .key-badge {
            color: #6c7086;
            font-size: 11px;
            font-weight: bold;
        }
        separator {
            background-color: #313244;
            min-height: 1px;
            margin: 4px 6px;
        }
        """
        style_provider = Gtk.CssProvider()
        style_provider.load_from_data(css)
        Gtk.StyleContext.add_provider_for_screen(
            Gdk.Screen.get_default(),
            style_provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )

        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
        self.add(main_box)

        menu_items = [
            ("🖵  Task Manager", "t", "task_manager"),
            ("⌨  Terminal", "x", "terminal"),
            None,
            ("🌙 Toggle Night Light", "n", "night_light"),
            ("🎤 Mute / Unmute Mic", "m", "mic_mute"),
            ("🔊 Mute / Unmute Audio", "a", "audio_mute"),
            ("🔕 Toggle Do Not Disturb", "d", "dnd"),
            None,
            ("🔒 Lock Screen", "l", "lock"),
            ("➔  Log Out", "k", "logout"),
            ("💤 Suspend / Sleep", "s", "suspend"),
            ("🗘  Restart", "r", "reboot"),
            ("⏻  Shut Down", "u", "shutdown")
        ]

        self.key_map = {}

        for item in menu_items:
            if item is None:
                sep = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
                main_box.pack_start(sep, False, False, 2)
                continue

            label_text, key, action = item
            self.key_map[key.lower()] = action

            btn = Gtk.Button()
            btn_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=16)

            lbl_title = Gtk.Label(label=label_text, xalign=0)
            lbl_title.set_hexpand(True)

            lbl_key = Gtk.Label(label=f"[{key}]")
            lbl_key.get_style_context().add_class("key-badge")

            btn_box.pack_start(lbl_title, True, True, 0)
            btn_box.pack_end(lbl_key, False, False, 0)
            btn.add(btn_box)

            btn.connect("clicked", lambda w, a=action: execute_action(a))
            main_box.pack_start(btn, False, False, 0)

        self.connect("focus-out-event", self.on_dismiss)
        self.connect("key-press-event", self.on_key_press)

    def on_dismiss(self, *args):
        Gtk.main_quit()
        sys.exit(0)

    def on_key_press(self, widget, event):
        key = Gdk.keyval_name(event.keyval)
        if not key:
            self.on_dismiss()
            return

        key = key.lower()
        if key in self.key_map:
            execute_action(self.key_map[key])
        else:
            self.on_dismiss()

if __name__ == "__main__":
    win = QuickMenu()
    win.show_all()
    Gtk.main()

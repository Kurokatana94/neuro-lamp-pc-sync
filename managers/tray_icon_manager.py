from PIL import Image, ImageDraw
from managers.settings_manager import UserSettings, SettingsWindow
import pystray
import threading
import os

class TrayIconManager:
    def __init__(self, app: function, settings_manager: UserSettings):
        self.app = app
        self.settings_manager = settings_manager
        self._settings_window_open = False
        self.on_icon = Image.open("assets/neuro-lava-lamp-sync-on-64x64.png")
        self.off_icon = Image.open("assets/neuro-lava-lamp-sync-off-64x64.png")
        self.base_icon = Image.open("assets/neuro-lava-lamp-sync-64x64.png")
        self.setup_tray()
    
    def on_exit(self, icon, item):
        icon.stop()
        os._exit(0)

    def setup_tray(self):
        icon = pystray.Icon(
            name="NeuroSync",
            icon=self.base_icon,
            title="Neuro Lamp Sync",
            menu=pystray.Menu(
                pystray.MenuItem("Settings", self.open_settings),
                pystray.MenuItem("Exit", self.on_exit),
            )
        )
        # icon.visible = True

        threading.Thread(target=self.app, daemon=True).start()

        icon.run()

    def open_settings(self, icon=None, item=None):
        if self._settings_window_open:
            return

        self._settings_window_open = True

        def run_settings_window():
            try:
                settings_window = SettingsWindow(self.settings_manager)
                settings_window.run()
            finally:
                self._settings_window_open = False

        threading.Thread(target=run_settings_window, daemon=True).start()

    def create_dummy_icon(self):
        image = Image.new('RGB', (64, 64), color = (0, 120, 215))
        dc = ImageDraw.Draw(image)
        dc.text((20, 20), "N", fill=(255, 255, 255))
        return image
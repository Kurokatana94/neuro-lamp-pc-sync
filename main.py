from managers.rgb_sync_manager import SyncManager
from managers.tray_icon_manager import TrayIconManager
from managers.settings_manager import UserSettings

user_settings = UserSettings()
sync_manager = SyncManager(user_settings)

# ===================== Main Loop =====================
def main_loop():
    while True:
        sync_manager.update_color()


if __name__ == "__main__":
    tray_icon_manager = TrayIconManager(main_loop, user_settings)
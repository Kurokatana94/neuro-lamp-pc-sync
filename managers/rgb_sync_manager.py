from openrgb import OpenRGBClient
from openrgb.utils import RGBColor
from managers.settings_manager import UserSettings
from pathlib import Path
import hPyT
import requests
import time
import random
import re

DEFAULT_PROFILE = 'neurosyncdefaultprofile'
config_settings = None

# test_hex_values = ["#ff0000", "#00ff00", "#0000ff", "#ffff00", "#ff00ff", "#00ffff", "#ffffff", "#000000"]

class SyncManager:
    def __init__(self, user_settings: UserSettings):
        self.client = OpenRGBClient()
        self.user_settings = user_settings
        self.devices = self.client.devices if len(self.client.devices) > 0 else None
        self.was_live = False
        self.last_hex = "#000000"

        # Dual swithcing method for SignalRGB Pro (not improvements to flickering -> paused)
        # self.target_html_file = 0

    def update_color(self, hex: str, live: bool):
        if self.user_settings.config["user_settings"]["rgb_software"] == "SignalRGB":
            self.signalrgb_update_color(hex, live)
        elif self.user_settings.config["user_settings"]["rgb_software"] == "OpenRGB":
            self.openrgb_update_color(hex, live)

    # ===================== OpenRGB Color Update =====================

    def openrgb_update_color(self, hex, live: bool):
        if self.devices:
            print("Updating colors...")
            try:
                # Legacy client code for testing without library

                # response = requests.get('http://api.neurolavalamp.com/v1/rgb')
                # response = response.json()
                # print(f"Response: {response}")
                # hex = response['hex']
                # hex = random.choice(test_hex_values) for testing
                
                if live:
                    if (self.was_live == False):
                        self.was_live = True
                        self.client.save_profile(DEFAULT_PROFILE)
                    if self.last_hex != hex:
                        self.fade_to_hex(
                            hex,
                            duration=self.user_settings.config["user_settings"]["duration"], 
                            steps=self.user_settings.config["user_settings"]["steps"])
                        self.last_hex = hex
                else:
                    if self.was_live:
                        self.was_live = False
                        self.reset_to_default()
            except Exception as e:
                print(f"Error: {e}")
        else:
            print("No devices found. Please check your OpenRGB connection.")
        
        # time.sleep(1 if self.was_live else 30)

    def reset_to_default(self):
        if self.user_settings.config["user_settings"]["rgb_software"] == "OpenRGB":
            if self.devices:
                self.client.update_profiles()
                try:
                    self.client.load_profile(DEFAULT_PROFILE)
                except:
                    print("Default profile not found, using OpenRGB default profile")
        else:
            print("Resetting to default colors...")
            self.signalrgb_update_color(self.last_hex, False)

    # ===================== SignalRGB Color Update ===================== 

    def signalrgb_update_color(self, hex, live: bool):
        if live != self.was_live:
            self.was_live = live
        
        self.signalrgb_effect_path = self.user_settings.get_signalrgb_effect_path()

        # Dual swithcing method for SignalRGB Pro (not improvements to flickering -> paused)
        # self.target_html_file = abs(self.target_html_file-1)

        # path_list = list(self.user_settings.get_signalrgb_effect_path())
        # path_list[-6] = str(self.target_html_file)
        # self.signalrgb_effect_path = ''.join(path_list)
        
        # print(self.signalrgb_effect_path)

        try:
            with open(self.signalrgb_effect_path, 'r', encoding='utf-8') as f:
                content = f.read()

            new_content = content
            current_hex = self.last_hex
            target_hex = self.last_hex

            if live:
                if not re.fullmatch(r"#[0-9A-Fa-f]{6}", hex):
                    print(f"Invalid hex color: {hex}")
                    return

                target_hex = hex
                duration_seconds = float(self.user_settings.config["user_settings"].get("duration", 0))
                speed_ms = max(0, int(duration_seconds * 1000))

                # Update currentColor and targetColor for the fade transition.
                color_pattern = r'(var\s+(currentColor|targetColor)\s*=\s*")[^"]*(";)'

                def replace_color_var(match):
                    var_name = match.group(2)
                    color_value = current_hex if var_name == "currentColor" else target_hex
                    return f'{match.group(1)}{color_value}{match.group(3)}'

                new_content, replacements = re.subn(
                    color_pattern,
                    replace_color_var,
                    new_content,
                    count=2,
                )

                if replacements < 2:
                    print("Could not find both currentColor and targetColor assignments in SignalRGB HTML.")
                    return

                new_content, speed_replacements = re.subn(
                    r'(var\s+speed\s*=\s*)\d+(\s*;)',
                    lambda match: f"{match.group(1)}{speed_ms}{match.group(2)}",
                    new_content,
                    count=1,
                )

                if speed_replacements == 0:
                    print("Could not find speed/steps assignments in SignalRGB HTML.")
                    return

            new_content, is_live_replacements = re.subn(
                r'(var\s+isLive\s*=\s*)(true|false)(\s*;)',
                lambda match: f"{match.group(1)}{'true' if live else 'false'}{match.group(3)}",
                new_content,
                count=1,
            )


            if is_live_replacements == 0:
                print("Could not find isLive assignment in SignalRGB HTML.")
                return

            with open(self.signalrgb_effect_path, 'w', encoding='utf-8') as f:
                f.write(new_content)

            if live:
                self.last_hex = target_hex
                print(
                    f"Updated colors: currentColor={current_hex}, targetColor={target_hex}, "
                    f"isLive={str(live).lower()}"
                )
            else:
                print("Updated SignalRGB effect: isLive=false")

            # Dual swithcing method for SignalRGB Pro (not improvements to flickering -> paused)
            # url = f"http://127.0.0.1:16038/api/v1/lighting/effects/{self.signalrgb_effect_path.split("\\")[-1]}/apply"

            # response = requests.post(url, json={})

            # print(f"Applied SignalRGB effect: {self.signalrgb_effect_path.split('\\')[-1]}, Response: {response.status_code} - {response.text}")

        except Exception as e:
            print(f"Failed to update HTML: {e}")
            self.signalrgb_effect_path = self.user_settings.get_signalrgb_effect_path()


    # ===================== Color Fading =====================

    @staticmethod
    def hex_to_rgb(hex_str):
        hex_str = hex_str.lstrip('#')
        return tuple(int(hex_str[i:i+2], 16) for i in (0, 2, 4))


    def fade_to_hex(self, target_hex, duration=0, steps=1):
        target = self.hex_to_rgb(target_hex)

        current = (0, 0, 0)
        if self.devices and len(self.devices) > 0 and self.devices[0].colors:
            c = self.devices[0].colors[0]
            current = (c.red, c.green, c.blue)

        delay = duration / steps

        for i in range(1, steps + 1):
            t = i / steps
            r = int(current[0] + (target[0] - current[0]) * t)
            g = int(current[1] + (target[1] - current[1]) * t)
            b = int(current[2] + (target[2] - current[2]) * t)

            color = RGBColor(r, g, b)
            print(f"Setting color to: {color}")
            for device in self.devices:
                device.set_color(color)
            # hPyT.border_color.set(color=f"#{r:02x}{g:02x}{b:02x}")

            time.sleep(delay)


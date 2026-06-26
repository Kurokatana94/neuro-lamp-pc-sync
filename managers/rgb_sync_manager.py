from openrgb import OpenRGBClient
from openrgb.utils import RGBColor
from managers.settings_manager import UserSettings
import hPyT
import requests
import time
import random

DEFAULT_PROFILE = 'neurosyncdefaultprofile'
config_settings = None

test_hex_values = ["#ff0000", "#00ff00", "#0000ff", "#ffff00", "#ff00ff", "#00ffff", "#ffffff", "#000000"]

class SyncManager:
    def __init__(self, user_settings: UserSettings):
        self.client = OpenRGBClient()
        self.user_settings = user_settings
        self.devices = self.client.devices if len(self.client.devices) > 0 else None
        self.was_live = False
        self.last_hex = None

    def update_color(self):
        if self.devices:
            print("Updating colors...")
            try:
                response = requests.get('http://api.neurolavalamp.com/v1/rgb')
                response = response.json()
                print(f"Response: {response}")
                hex = response['hex']
                # hex = random.choice(test_hex_values) for testing
                
                if response['live']:
                    if (self.was_live == False):
                        self.was_live = True
                        self.client.save_profile(DEFAULT_PROFILE)
                    if self.last_hex != hex:
                        self.fade_to_hex(hex, duration=self.user_settings.config["user_settings"]["duration"], steps=self.user_settings.config["user_settings"]["steps"])
                        self.last_hex = hex
                else:
                    if self.was_live:
                        self.was_live = False
                        self.client.update_profiles()
                        try:
                            self.client.load_profile(DEFAULT_PROFILE)
                        except:
                            print("Default profile not found, using OpenRGB default profile")
            
            except Exception as e:
                print(f"Error: {e}")
        else:
            print("No devices found. Please check your OpenRGB connection.")
        
        time.sleep(1 if self.was_live else 30)
            

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
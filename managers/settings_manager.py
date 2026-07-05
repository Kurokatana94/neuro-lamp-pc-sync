import customtkinter as ctk
from tkinter import filedialog
from pathlib import Path
import hPyT
import winreg as reg
import sys
import json
import os

ctk.set_appearance_mode("light")


def resource_path(*parts: str) -> str:
    base_path = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent.parent))
    return str(base_path.joinpath(*parts))


ctk.set_default_color_theme(resource_path("assets", "themes", "neuro_theme.json"))

class UserSettings:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        appdata_dir = Path(os.getenv("APPDATA", str(Path.home()))) / "NeuroLampSync"
        appdata_dir.mkdir(parents=True, exist_ok=True)
        self.config_path = appdata_dir / "config.json"

        # Backward compatibility: migrate local config if present and AppData config is missing.
        local_config = Path("config.json")
        if not self.config_path.exists() and local_config.exists():
            try:
                self.config_path.write_text(local_config.read_text(encoding="utf-8"), encoding="utf-8")
            except Exception:
                pass

        self.config = self.load_settings()
        self._initialized = True
    
    def load_settings(self):
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config_settings = json.load(f)
                print(f"Config settings: {config_settings}")
        except (FileNotFoundError, json.JSONDecodeError):
            print("Config file not found. Using default settings.")
            config_settings = self.create_new_config()

        return config_settings
    
    #===================== Create New Config =====================
    def create_new_config(self):
        '''
        Safety-net that creates a new config.json file with default settings if it doesn't exist.
        '''
        self.default_config = {
            "user_settings": {
                "rgb_software": "OpenRGB",
                "ip_address": "127.0.0.1",
                "port": 6742,
                "run_on_startup": False,
                "effect": "direct",
                "duration": 0,
                "steps": 1,
                "signalrgb_effect_path": None
            },
            "openrgb_default_profile": "default",
            "rgb_supported_softwares": [
                "OpenRGB",
                "SignalRGB"
            ],
            "supported_effects": {
                "openrgb": [
                    "direct",
                    "fade"
                ],
                "signalrgb": [
                    "direct"
                ]
            },
            "effects": {
                "direct": {
                    "duration": 0,
                    "steps": 1
                },
                "fade": {
                    "duration": 0.8,
                    "steps": 20
                }
            }
        }
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(self.default_config, f, indent=4)
        except Exception as e:
            print(f"Error creating config file: {e}")
        
        return self.default_config
    
    # ==================== Save Settings =====================

    def save_settings(self, new_user_settings: dict) -> dict:
        try:
            self.config["user_settings"] = new_user_settings
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=4)

            return {"success": True, "message": "Settings saved successfully."}
        except Exception as e:
            print(f"Error saving config file: {e}")
            return {"success": False, "message": f"Error saving settings: {e}"}

    # ==================== Set Settings =====================

    def get_signalrgb_effect_path(self) -> str | None:
        if not self.config["user_settings"].get("signalrgb_effect_path"):
            effect_name = "NeuroLampSync.html"
            signalrgb_effects_dir = Path.home() / "Documents" / "WhirlwindFX" / "Effects"
            file_path = signalrgb_effects_dir / effect_name
            self.config["user_settings"]["signalrgb_effect_path"] = str(file_path)
            self.save_settings(self.config["user_settings"])
        else:
            file_path = Path(self.config["user_settings"]["signalrgb_effect_path"])

        return str(file_path)

    def set_startup_state(self, state: bool):
        try:
            key = reg.OpenKey(reg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run", 0, reg.KEY_SET_VALUE)

            if state:
                if getattr(sys, "frozen", False):
                    startup_command = f'"{Path(sys.executable).resolve()}"'
                else:
                    startup_command = f'"{Path(sys.executable).resolve()}" "{Path(sys.argv[0]).resolve()}"'

                reg.SetValueEx(key, "NeuroLampSync", 0, reg.REG_SZ, startup_command)
            else:
                try:
                    reg.DeleteValue(key, "NeuroLampSync")
                except FileNotFoundError:
                    pass

            reg.CloseKey(key)
            return {"success": True, "message": "Startup setting updated."}
        except Exception as e:
            print(f"Error setting startup state: {e}")
            return {"success": False, "message": f"Error updating startup setting: {e}"}

    def reset_to_default(self):
        try:
            self.config = self.create_new_config()
            return {"success": True, "message": "Settings reset to default successfully."}
        except Exception as e:
            print(f"Error resetting settings to default: {e}")
            return {"success": False, "message": f"Error resetting settings: {e}"}
            


class SettingsWindow:
    def __init__(self, settings_manager):
        self.settings_manager: UserSettings = settings_manager
        self.settings: dict = self.settings_manager.config["user_settings"]
        self.root = ctk.CTk()

        self.root.title("Neuro Lamp Sync - Settings")
        self.root.geometry("500x450")
        self.root.resizable(False, False)

        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        
        self.root.geometry(f"{width}x{height}+{x}+{y}")

        hPyT.title_bar_color.set(self.root, color="#85e1e7")
        hPyT.border_color.set(self.root, color="#85e1e7")

        self.root.grid_columnconfigure(1, weight=1)

        self.root.iconbitmap(resource_path("assets", "neuro-lava-lamp-sync-256x256.ico"))

        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

        self.duration_validate_cmd = (self.root.register(self._validate_duration_input), "%P")
        self.int_validate_cmd = (self.root.register(self._validate_positive_int_input), "%P")

        self.create_widgets()
        self.init_styles()
    
    def init_styles(self):
        # Keep this method for future per-instance style setup.
        pass

    # All options will load at init, but will be hidden after initial settings check
    def create_widgets(self):
        row = 0
        label_column = 0
        input_column = 1

        # ============================= Title =============================
        ctk.CTkLabel(self.root, 
            text="Settings", 
            font=ctk.CTkFont(size=24, weight="bold")
            ).grid(row=row, column=label_column, columnspan=2, pady=20, padx=10)
        row += 1
        
        # ============================= Run at startup =============================
        self.startup_var = ctk.BooleanVar(value=self.settings["run_on_startup"])
        ctk.CTkLabel(self.root, text="Run at startup:"
            ).grid(row=row, column=label_column, pady=4, padx=10, sticky="w")
        ctk.CTkSwitch(self.root, 
            text="", 
            variable=self.startup_var,
            command=self.on_startup_toggle,
            switch_width=60,
            switch_height=28,
            ).grid(row=row, column=input_column, pady=4, padx=10, sticky="e")
        row += 1
        
        # ============================= RGB Software Selection =============================
        ctk.CTkLabel(self.root, text="RGB Software:").grid(row=row, column=label_column, pady=4, padx=10, sticky="w")
        self.rgb_software_var = ctk.StringVar(value=self.settings["rgb_software"])
        self.rgb_software_dropdown = ctk.CTkOptionMenu(self.root,
            variable=self.rgb_software_var,
            values=self.settings_manager.config["rgb_supported_softwares"],
            command=self.on_rgb_software_change
            )
        self.rgb_software_dropdown.grid(row=row, column=input_column, pady=4, padx=10, sticky="e")
        row += 1

        # ============================= Effect Selection =============================
        self.effect_label = ctk.CTkLabel(self.root, text="Effect:")
        self.effect_label.grid(row=row, column=label_column, pady=4, padx=10, sticky="w")
        
        self.effect_var = ctk.StringVar(value=str(self.settings["effect"]).capitalize())
        self.effect_dropdown = ctk.CTkOptionMenu(self.root,
            variable=self.effect_var,
            values=[value.capitalize() for value in self.settings_manager.config["supported_effects"][self.rgb_software_var.get().lower()]],
            command=self.on_effect_change
            )
        self.effect_dropdown.grid(row=row, column=input_column, pady=4, padx=10, sticky="e")
        row += 1

        # =========

        # These options will show only for specific effects
        self.duration_label = ctk.CTkLabel(self.root, text="Duration: ")
        self.duration_label.grid(row=row, column=label_column, pady=4, padx=10, sticky="w")
        self.duration_var = ctk.DoubleVar(
            value=float(self.settings_manager.config["effects"][str(self.effect_var.get()).lower()]["duration"])
        )
        self.duration_entry = ctk.CTkEntry(self.root,
            textvariable=self.duration_var,
            validate="key",
            validatecommand=self.duration_validate_cmd
            )
        self.duration_entry.grid(row=row, column=input_column, pady=4, padx=10, sticky="e")
        row += 1

        # =========

        self.steps_label = ctk.CTkLabel(self.root, text="Steps: ")
        self.steps_label.grid(row=row, column=label_column, pady=4, padx=10, sticky="w")

        self.steps_var = ctk.IntVar(
            value=int(self.settings_manager.config["effects"][str(self.effect_var.get()).lower()]["steps"])
        )

        self.steps_entry = ctk.CTkEntry(self.root,
            textvariable=self.steps_var,
            validate="key",
            validatecommand=self.int_validate_cmd
            )
        self.steps_entry.grid(row=row, column=input_column, pady=4, padx=10, sticky="e")
        row += 1

        # ============================= Effect Path (only for SignalRGB) =============================

        self.effect_path_label = ctk.CTkLabel(self.root, text="Effect Path:")
        self.effect_path_label.grid(row=row, column=label_column, pady=4, padx=10, sticky="w")
        
        self.effect_path_frame = ctk.CTkFrame(self.root, fg_color="transparent")
        self.effect_path_frame.grid(row=row, column=input_column, pady=4, padx=10, sticky="ew")
        self.effect_path_frame.grid_columnconfigure(0, weight=1)

        self.effect_path_var = ctk.StringVar(
            value=self.settings["signalrgb_effect_path"] if self.settings["signalrgb_effect_path"] else ""
        )
        self.effect_path_entry = ctk.CTkEntry(self.effect_path_frame, textvariable=self.effect_path_var)
        self.effect_path_entry.grid(row=0, column=0, sticky="ew")

        self.effect_path_browse_button = ctk.CTkButton(self.effect_path_frame, text="...", command=self.on_browse_path,
            width=32,
            corner_radius=8)
        self.effect_path_browse_button.grid(row=0, column=1, padx=(8, 0), sticky="e")
        row += 1

        # ============================= IP Address (only for OpenRGB) =============================
        self.ip_address_label = ctk.CTkLabel(self.root, text="IP Address:")
        self.ip_address_label.grid(row=row, column=label_column, pady=4, padx=10, sticky="w")
        
        self.ip_address_var = ctk.CTkEntry(self.root, 
            textvariable=ctk.StringVar(
                value=self.settings["ip_address"]))
        self.ip_address_var.grid(row=row, column=input_column, pady=4, padx=10, sticky="e")
        row += 1

        # ============================= Port (only for OpenRGB) =============================
        self.port_label = ctk.CTkLabel(self.root, text="Port:")
        self.port_label.grid(row=row, column=label_column, pady=4, padx=10, sticky="w")
        
        self.port_var = ctk.CTkEntry(self.root, 
            textvariable=ctk.StringVar(
                value=self.settings["port"]
                ),
            validate="key",
            validatecommand=self.int_validate_cmd
            )
        self.port_var.grid(row=row, column=input_column, pady=4, padx=10, sticky="e")
        row +=1

        # ============================= Save Button =============================
        ctk.CTkButton(self.root, 
            text="Save", 
            command=self.on_save
            ).grid(row=row, column=label_column, columnspan=2, pady=8, padx=10)
        row += 1

        # ============================= Reset Button =============================
        ctk.CTkButton(self.root, 
            text="Reset to Default", 
            command=self.on_reset
            ).grid(row=row, column=label_column, columnspan=2, pady=8, padx=10)
        row += 1
        
        self.message_label = ctk.CTkLabel(self.root, text="", text_color="red")
        self.message_label.grid(row=row, column=label_column, columnspan=2, pady=4, padx=10)

        self.on_effect_change()

        # Initial visibility of IP and Port fields based on selected software
        self.on_rgb_software_change()

    # ============================= Event Handlers =============================
    def on_rgb_software_change(self, selected_software=None):
        self.on_error("")

        if selected_software is not None:
            self.rgb_software_var.set(selected_software)
        selected_software = self.rgb_software_var.get()
        self.settings["rgb_software"] = selected_software
        result = self.settings_manager.save_settings(self.settings)

        if not result["success"]:
            self.on_error(result["message"])
        
        if selected_software == "OpenRGB":
            self.ip_address_label.grid()
            self.ip_address_var.grid()
            
            self.port_label.grid()
            self.port_var.grid()

            self.effect_path_label.grid_remove()
            self.effect_path_frame.grid_remove()

            self.repopulate_effect_dropdown()
        else:
            self.ip_address_label.grid_remove()
            self.ip_address_var.grid_remove()

            self.port_label.grid_remove()
            self.port_var.grid_remove()

            self.effect_path_label.grid()
            self.effect_path_frame.grid()

            self.repopulate_effect_dropdown()

            # self.on_error("To use SignalRGB you must have a PRO account.")

    def repopulate_effect_dropdown(self):
        current_effect = self.effect_var.get()
        supported_effects = self.settings_manager.config["supported_effects"][self.rgb_software_var.get().lower()]
        self.effect_dropdown.configure(values=[effect.capitalize() for effect in supported_effects])
        
        if current_effect.lower() not in supported_effects:
            self.effect_var.set(supported_effects[0].capitalize())
            self.on_effect_change(supported_effects[0].capitalize())

    def _sync_user_effect_values(self, effect_name: str):
        effect_settings = self.settings_manager.config["effects"][effect_name]
        self.settings["duration"] = effect_settings["duration"]
        self.settings["steps"] = effect_settings["steps"]

    def _set_effect_input_values(self, effect_name: str):
        effect_settings = self.settings_manager.config["effects"][effect_name]
        self.duration_var.set(float(effect_settings["duration"]))
        self.steps_var.set(int(effect_settings["steps"]))

    def _validate_duration_input(self, proposed_value: str) -> bool:
        # Keep numeric variables valid at all times and block letters/symbol noise.
        if proposed_value == "":
            return False

        if proposed_value.count(".") > 1:
            return False

        try:
            value = float(proposed_value)
        except ValueError:
            return False

        return value >= 0

    def _validate_positive_int_input(self, proposed_value: str) -> bool:
        if proposed_value == "":
            return False

        if not proposed_value.isdigit():
            return False

        return int(proposed_value) >= 1

    def on_effect_change(self, selected_effect=None):
        self.on_error("")
        if selected_effect is not None:
            self.effect_var.set(selected_effect)
        selected_effect = str(self.effect_var.get()).lower()
        self._set_effect_input_values(selected_effect)
        self.settings["effect"] = selected_effect
        self._sync_user_effect_values(selected_effect)
        result = self.settings_manager.save_settings(self.settings)

        if not result["success"]:
            self.on_error(result["message"])

        if selected_effect == "fade":
            self.duration_label.grid()
            self.duration_entry.grid()

            if self.rgb_software_var.get() == "OpenRGB":
                self.steps_label.grid()
                self.steps_entry.grid()
            else:
                self.steps_label.grid_remove()
                self.steps_entry.grid_remove()
        else:
            self.duration_label.grid_remove()
            self.duration_entry.grid_remove()
            
            self.steps_label.grid_remove()
            self.steps_entry.grid_remove()

    def on_startup_toggle(self):
        self.on_error("")
        new_state = self.startup_var.get()
        self.settings["run_on_startup"] = new_state
        result = self.settings_manager.save_settings(self.settings)

        if not result["success"]:
            self.on_error(result["message"])
            self.startup_var.set(not new_state)
            self.settings["run_on_startup"] = not new_state
            return

        startup_result = self.settings_manager.set_startup_state(new_state)
        if not startup_result["success"]:
            self.on_error(startup_result["message"])
            # Revert toggle and persisted state when startup registration fails.
            self.startup_var.set(not new_state)
            self.settings["run_on_startup"] = not new_state
            self.settings_manager.save_settings(self.settings)

    def on_save(self):
        self.on_error("")
        self.settings["effect"] = str(self.effect_var.get()).lower()
        self.settings["rgb_software"] = self.rgb_software_var.get()
        self.settings["ip_address"] = self.ip_address_var.get()
        self.settings["port"] = int(self.port_var.get())
        self.settings["run_on_startup"] = self.startup_var.get()
        self.settings["signalrgb_effect_path"] = self.effect_path_var.get() if self.effect_path_var.get() else None

        # Update effect settings
        selected_effect = self.settings["effect"]
        effect_settings = self.settings_manager.config["effects"][selected_effect]
        if self.settings["effect"] == "fade":
            effect_settings["duration"] = float(self.duration_entry.get())
            effect_settings["steps"] = int(self.steps_entry.get())

        self._sync_user_effect_values(selected_effect)

        result = self.settings_manager.save_settings(self.settings)

        if not result["success"]:
            self.on_error(result["message"])
        else:
            self.message_label.configure(text="Saved!", text_color="green")

    def on_browse_path(self):
        file_path = filedialog.askopenfilename(filetypes=[("HTML files", "*.html")], initialdir=Path.home() / "Documents" / "WhirlwindFX" / "Effects", title="Select SignalRGB Effect HTML File")
        if file_path:
            self.effect_path_var.set(file_path)

    def on_reset(self):
        self.on_error("")
        result = self.settings_manager.reset_to_default()

        if not result["success"]:
            self.on_error(result["message"])

        self.settings = self.settings_manager.config["user_settings"]
        self.on_rgb_software_change(self.settings["rgb_software"])
        self.on_effect_change(self.settings["effect"].capitalize())
        self.startup_var.set(self.settings["run_on_startup"])
        self.on_startup_toggle()

    def on_error(self, message):
        self.message_label.configure(text=message)

    def on_close(self):
        self.root.quit()
        self.root.destroy()

    def run(self):
        self.root.mainloop()
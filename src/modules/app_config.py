# This file is part of PYZ-LAUNCHER-FOR-MINECRAFT (https://github.com/ZadkielAvendano/PyZ-Launcher-for-Minecraft)
# Copyright (c) 2025 Zadkiel Avendano and collaborators
# License-Identifier: MIT License

import flet as ft
from enum import Enum
import random
import uuid
import os
import pathlib
import platform

app_name = "PyZ Launcher"
app_version = "0.3.0_dev1" # Enter 'dev' in the name to test
dev_mode = True if "dev" in app_version else False

SETTINGS_KEY = "pyz.minecraftlauncher.settings"

default_data = {
    "username": f"Player{random.randrange(100, 1000)}",
    "uuid": str(uuid.uuid4()),
    "token": "", # Offline,
    "lastPlayed": "", # ID of the last version of Minecraft played
    "minecraftDirectory": "", # Empty for the default Minecraft directory
    "executablePath": "", # Empty for the default Java directory
    "jvmArguments": ["-Xmx2G", "-Xms2G"] # JVM Arguments
    }

try:
    FLET_APP_STORAGE_DATA = os.getenv("FLET_APP_STORAGE_DATA")
    FLET_APP_STORAGE_TEMP = os.getenv("FLET_APP_STORAGE_TEMP")
except Exception as e:
    print(f"Error: {e}")

class AppData(Enum):
    """
    Defines an enumeration for various application settings for Minecraft.
    """
    USERNAME = "username"
    UUID = "uuid"
    TOKEN = "token"
    LAST_PLAYED = "lastPlayed"
    MC_DIRECTORY = "minecraftDirectory"
    EXECUTABLE_PATH = "executablePath"
    JVM_ARGUMENTS = "jvmArguments"


class Settings():
    """
    Manages application settings, including loading, saving, and retrieving stored configurations.
    """
    def __init__(self, page: ft.Page = None, settings: dict = None):
        self.page = page
        self.settings = settings

    def load_settings(self):
        """
        Loads saved settings from client storage or initializes them with default values if none exist.
        """
        if self.page.client_storage.contains_key(SETTINGS_KEY):
            self.settings = self.page.client_storage.get(SETTINGS_KEY)
        else:
            self.page.client_storage.set(SETTINGS_KEY, default_data)
            self.settings = self.page.client_storage.get(SETTINGS_KEY)
        print(f"Settings loaded: {self.settings}")

    def save_settings(self, key: AppData, save: str):
        """
        Saves a specific setting to client storage, handling errors gracefully.
        """
        try:
            self.settings[key.value] = save
            self.page.client_storage.set(SETTINGS_KEY, self.settings)
            self.settings = self.page.client_storage.get(SETTINGS_KEY)
            print(f"Settings saved: {self.settings}")
        except Exception as e:
            print(f"An error occurred while saving data. {e}")

    def get_setting(self, setting: AppData):
        """
        Retrieves the value of a specified setting, ensuring it exists by initializing it if necessary.
        """
        try:
            return self.settings[setting.value]
        except Exception as e:
            print(f"Data type not found. {e}")
            self.save_settings(setting, default_data[setting.value])
            return default_data[setting.value]
        
    def return_mc_directory(self) -> str:
        """
        Returns the correct Minecraft directory path based on system type or developer mode settings.
        """
        minecraft_directory = self.get_setting(AppData.MC_DIRECTORY)
        try:
            if minecraft_directory == "" and not dev_mode: # Default Minecraft Directory
                if platform.system() == "Windows":
                    return os.path.join(os.getenv("APPDATA", os.path.join(pathlib.Path.home(), "AppData", "Roaming")), ".minecraft")
                elif platform.system() == "Darwin":
                    return os.path.join(str(pathlib.Path.home()), "Library", "Application Support", "minecraft")
                else:
                    return os.path.join(str(pathlib.Path.home()), ".minecraft")
                
            elif minecraft_directory == "" and dev_mode: # Default directory for developer mode (Recommended)
                minecraft_directory = os.path.join(os.getcwd(), "minecraft_data") # Test
                if not os.path.exists(minecraft_directory):
                    os.makedirs(minecraft_directory)
                return minecraft_directory

            else:
                if not os.path.exists(minecraft_directory):
                    os.makedirs(minecraft_directory)
                return minecraft_directory
            
        except Exception as e:
            print(f"Error: {e}")
            return ""

            

app_settings = Settings()

def init_settings(page: ft.Page):
    """
    Initializes application settings for the given UI page and ensures Minecraft directory availability.
    """
    app_settings.page = page
    app_settings.load_settings()
    print("MINECRAFT DIRECTORY:", app_settings.return_mc_directory())
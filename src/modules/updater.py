# This file is part of PYZ-LAUNCHER-FOR-MINECRAFT (https://github.com/ZadkielAvendano/PyZ-Launcher-for-Minecraft)
# Copyright (c) 2026 Zadkiel Avendano and collaborators
# License-Identifier: MIT License

from modules.app_config import app_version, LAUNCHER_REPOSITORY_API
import requests

def has_update() -> bool | str:
    try:
        response = requests.get(f"{LAUNCHER_REPOSITORY_API}/releases/latest")
        if response.status_code == 200:
            data: dict = response.json()
            latest_version = data.get("tag_name", app_version)
            print(f"Latest version: {latest_version}, Current version: {app_version}")
            return latest_version != app_version, app_version if latest_version == app_version else latest_version, f""
        else:
            print(f"Failed to fetch update info: {response.status_code}")
            return False, app_version
    except Exception as e:
        print(f"Error checking for updates: {e}")
        return False, app_version
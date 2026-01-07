from modules.app_config import LAUNCHER_REPOSITORY_API, app_version

import os
import sys
import subprocess
import platform
import psutil
import requests

def has_update() -> bool | str:
    try:
        response = requests.get(f"{LAUNCHER_REPOSITORY_API}/releases/latest")
        if response.status_code == 200:
            data: dict = response.json()
            latest_version = data.get("tag_name", app_version)
            print(f"Latest version: {latest_version}, Current version: {app_version}")
            return latest_version != app_version, app_version if latest_version == app_version else latest_version
        else:
            print(f"Failed to fetch update info: {response.status_code}")
            return False, app_version
    except Exception as e:
        print(f"Error checking for updates: {e}")
        return False, app_version

def system_ram():
    '''
    Returns system RAM information.
    '''
    return {
        "total": psutil.virtual_memory().total // (1024**3),  # Total RAM in GB
        "available": psutil.virtual_memory().available // (1024**3),  # Available RAM in GB
        "percent": psutil.virtual_memory().percent,  # Percentage of used RAM
        "used": psutil.virtual_memory().used // (1024**3),  # Used RAM in GB
        "free": psutil.virtual_memory().free // (1024**3)  # Free RAM in GB
    }

def get_app_path():
    # Si la app está congelada (empaquetada como ejecutable)
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    # Si se ejecuta como script normal .py
    else:
        return os.path.dirname(os.path.abspath(__file__))

def open_file(file):
    '''
    Opens a file with the default application based on the operating system.
    '''
    try:
        file = os.path.abspath(file)
        if not os.path.exists(file):
            print(f"The file does not exist: {file}")
            return
        system = platform.system()
        if system == 'Windows':
            os.startfile(file)
        elif system == 'Darwin':  # macOS
            subprocess.run(['open', file])
        elif system == 'Linux':
            subprocess.run(['xdg-open', file])
        else:
            print(f'Unsupported system:: {system}')
    except Exception as e:
        print(f"An error occurred while trying to open the file: {file}.\nError: {e}")
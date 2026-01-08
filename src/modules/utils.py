# This file is part of PYZ-LAUNCHER-FOR-MINECRAFT (https://github.com/ZadkielAvendano/PyZ-Launcher-for-Minecraft)
# Copyright (c) 2026 Zadkiel Avendano and collaborators
# License-Identifier: MIT License

import subprocess
import platform
import psutil
import sys
import os

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
    try:
        return os.path.dirname(sys.executable)
    except Exception as e:
        print(f"Error getting app path: {e}")
        return None

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
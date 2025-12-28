import os
import subprocess
import platform
import psutil

def system_ram():
    return {
        "total": psutil.virtual_memory().total // (1024**3),  # Total RAM in GB
        "available": psutil.virtual_memory().available // (1024**3),  # Available RAM in GB
        "percent": psutil.virtual_memory().percent,  # Percentage of used RAM
        "used": psutil.virtual_memory().used // (1024**3),  # Used RAM in GB
        "free": psutil.virtual_memory().free // (1024**3)  # Free RAM in GB
    }

print(f"System RAM: {system_ram()['total']} GB")
print(f"Available RAM: {system_ram()['available']} GB")
print(f"Percentage RAM: {system_ram()['percent']} %")
print(f"Used RAM: {system_ram()['used']} GB")
print(f"Free RAM: {system_ram()['free']} GB")

def open_file(file):
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
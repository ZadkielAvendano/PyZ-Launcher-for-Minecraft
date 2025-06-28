import os
import subprocess
import platform

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
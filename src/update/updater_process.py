# This file is part of PYZ-LAUNCHER-FOR-MINECRAFT (https://github.com/ZadkielAvendano/PyZ-Launcher-for-Minecraft)
# Copyright (c) 2026 Zadkiel Avendano and collaborators
# License-Identifier: MIT License

# This file is executed as a separate process to handle the update installation.
# It waits for the main application to close, then replaces the necessary files,
# and finally restarts the main application.

# Compiled with PyInstaller.

import sys
import os
import time
import zipfile
import shutil
import subprocess
import platform

def show_message(title, message, is_error=False):
    """
    It displays a native pop-up window depending on the operating system.
    """
    system_os = platform.system()

    try:
        if system_os == "Windows":
            import ctypes
            # 0x40 = Info, 0x10 = Error
            style = 0x10 if is_error else 0x40
            ctypes.windll.user32.MessageBoxW(0, message, title, style)

        elif system_os == "Darwin":  # macOS
            icon = "stop" if is_error else "note"
            script = f'display dialog "{message}" with title "{title}" buttons {{"OK"}} default button "OK" with icon {icon}'
            subprocess.run(['osascript', '-e', script], check=False)

        elif system_os == "Linux":
            try:
                # Zenity (GNOME/Ubuntu/Standard)
                msg_type = '--error' if is_error else '--info'
                subprocess.run(['zenity', msg_type, '--text', message, '--title', title], 
                             check=False, stderr=subprocess.DEVNULL)
            except FileNotFoundError:
                try:
                    # KDialog (KDE)
                    msg_type = '--error' if is_error else '--msgbox'
                    subprocess.run(['kdialog', msg_type, message, '--title', title], 
                                 check=False, stderr=subprocess.DEVNULL)
                except FileNotFoundError:
                    print(f"\n[{title.upper()}] {message}\n")

        else:
            print(f"\n[{title.upper()}] {message}\n")

    except Exception as e:
        print(f"Error showing graphical alert: {e}")
        print(f"[{title}] {message}")



def main():
    # Arguments passed from the main app:
    # 1: Path to the downloaded ZIP file
    # 2: Path to the main executable (launcher.exe)
    
    if len(sys.argv) < 3:
        print("Usage: updater.exe <zip_path> <main_exe_path>")
        time.sleep(2)
        sys.exit(1)

    zip_path = sys.argv[1]
    main_exe_path = sys.argv[2]
    base_dir = os.path.dirname(main_exe_path)
    temp_extract_folder = os.path.join(base_dir, "temp_update_extract")

    print(f"Target: {main_exe_path}")
    print("Waiting for main application to close...")
    
    # --- WAIT FOR FILE LOCK RELEASE ---
    max_retries = 10
    for i in range(max_retries):
        try:
            test_rename = main_exe_path + ".check"
            if os.path.exists(main_exe_path):
                os.rename(main_exe_path, test_rename)
                os.rename(test_rename, main_exe_path)
            break
        except OSError:
            print(f"Waiting for file release... ({i+1}/{max_retries})")
            time.sleep(1)
    
    try:
        # Extract ZIP
        print(f"Extracting update to {temp_extract_folder}...")
        if os.path.exists(temp_extract_folder):
            shutil.rmtree(temp_extract_folder)
        
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(temp_extract_folder)
            
        # Overwrite files in the main directory
        print("Overwriting files...")
        for root, dirs, files in os.walk(temp_extract_folder):
            rel_path = os.path.relpath(root, temp_extract_folder)
            dest_folder = os.path.join(base_dir, rel_path)
            
            if not os.path.exists(dest_folder):
                os.makedirs(dest_folder)
                
            for file in files:
                src_file = os.path.join(root, file)
                dest_file = os.path.join(dest_folder, file)
                
                # CRITICAL: Do not try to overwrite the updater itself if it's running
                if os.path.abspath(dest_file) == os.path.abspath(sys.argv[0]):
                    continue

                if os.path.exists(dest_file):
                    try:
                        os.remove(dest_file)
                    except Exception as e:
                        print(f"Warning removing {dest_file}: {e}")

                shutil.copy2(src_file, dest_file)

        # Cleanup
        print("Cleaning up...")
        try:
            shutil.rmtree(temp_extract_folder)
            if os.path.exists(zip_path):
                os.remove(zip_path)
        except Exception as cleanup_error:
            print(f"Minor cleanup error: {cleanup_error}")

        print("Update applied successfully.")
        
        # --- OUTPUT ---
        show_message(
            "Update Completed", 
            "The update has been applied successfully.\nYou can start the launcher again.", 
            is_error=False
        )
        sys.exit(0)

    except Exception as e:
        print(f"Update failed: {e}")
        show_message(
            "Update Error", 
            f"An error occurred while applying the update:\n{e}", 
            is_error=True
        )
        sys.exit(1)

if __name__ == "__main__":
    main()
# This file is part of PYZ-LAUNCHER-FOR-MINECRAFT (https://github.com/ZadkielAvendano/PyZ-Launcher-for-Minecraft)
# Copyright (c) 2026 Zadkiel Avendano and collaborators
# License-Identifier: MIT License

import flet as ft
from modules.app_config import *
from modules.utils import *
import requests
import os
import time
import sys
import subprocess
import logging
import shutil

# ----- UI Helper Functions -----

def __update_status_safe(page: ft.Page, control, message):
    """Update a Flet control safely from a thread."""
    if page and control:
        control.value = message
        try:
            page.update()
        except Exception:
            pass

def __set_controls_enabled_safe(page: ft.Page, controls, enabled):
    """Safely enable or disable Flet controls."""
    if page:
        for control in controls:
            control.disabled = not enabled
        try:
            page.update()
        except Exception:
            pass

def __update_progress_safe(page: ft.Page, progress_bar: ft.ProgressBar, progress_text: ft.Text, downloaded: int, total: int):
    """Update progress bar safely."""
    if page and progress_bar and total > 0:
        ratio = downloaded / total
        page.window.progress_bar = ratio
        progress_bar.value = ratio
        if progress_text:
            pct = ratio * 100
            downloaded_mb = downloaded / (1024 * 1024)
            total_mb = total / (1024 * 1024)
            progress_text.value = f"{pct:.1f}% ({downloaded_mb:.2f} MB / {total_mb:.2f} MB)"
        try:
            page.update()
        except Exception:
            pass

# ----- Updater Logic -----

def check_link_exists(url) -> bool:
    try:
        response = requests.head(url, allow_redirects=True)
        if response.status_code == 200:
            print("The link exists!")
            return True
        else:
            print("The link is not available. Status code:", response.status_code)
            return False
    except requests.RequestException as e:
        print("Error while checking the link:", e)
        return False


def has_update() -> tuple[bool, str, str]:
    try:
        if dev_mode:
            return False, app_version
        response = requests.get(f"{LAUNCHER_REPOSITORY_API}/releases/latest")
        if response.status_code == 200:
            data: dict = response.json()
            latest_version = data.get("tag_name", app_version)
            print(f"Latest version: {latest_version}, Current version: {app_version}")
            return latest_version != app_version, app_version if latest_version == app_version else latest_version
        else:
            print(f"Failed to fetch update info: {response.status_code}")
            return False, app_version, "Error checking API"
    except Exception as e:
        print(f"Error checking for updates: {e}")
        return False, app_version, str(e)


def download_launcher_update(latest_version: str, page: ft.Page, status_text: ft.Text, progress_bar: ft.ProgressBar, progress_text: ft.Text,
                    buttons_to_disable: list, dialog: ft.AlertDialog):
    """
    Downloads the update interacting with the Flet UI similar to launcher.py
    """
    try:
        __set_controls_enabled_safe(page, buttons_to_disable, False)
        __update_status_safe(page, status_text, "Initializing download...")
        
        download_url = f"{LAUNCHER_REPOSITORY}/releases/download/{latest_version}/pyz_launcher_{latest_version}_{app_settings.page.platform.name.lower()}_portable.zip"
        # download_url = f"{LAUNCHER_REPOSITORY}/releases/download/v0.4.0-alpha/pyz_launcher_v0.4.0_portable.zip" # test link
        
        if not check_link_exists(download_url):
            raise Exception("Update download link not found.")

        __update_status_safe(page, status_text, "Downloading update...")
        page.window.progress_bar = 0
        response = requests.get(download_url, stream=True)
        response.raise_for_status()
        total_size = int(response.headers.get('content-length', 0))
        downloaded_size = 0

        # Ensure temporary directory exists
        if not os.path.exists(FLET_APP_STORAGE_TEMP):
            raise Exception("Temporary storage path not found.")

        temp_file_path = os.path.join(FLET_APP_STORAGE_TEMP, "update.zip")

        with open(temp_file_path, 'wb') as file:
            for data in response.iter_content(chunk_size=4096):
                file.write(data)
                downloaded_size += len(data)
                __update_progress_safe(page, progress_bar, progress_text, downloaded_size, total_size)

        __update_status_safe(page, status_text, "Download completed successfully!")
        time.sleep(1)
        install_update_and_restart(temp_file_path, page, status_text)

    except Exception as e:
        error_msg = f"Error downloading update: {str(e)}"
        print(error_msg)
        __update_status_safe(page, status_text, error_msg)
        
    finally:
        time.sleep(2)
        page.window.progress_bar = 0
        if dialog:
            page.close(dialog)
        __set_controls_enabled_safe(page, buttons_to_disable, True)


def install_update_and_restart(zip_path: str, page: ft.Page, status_text: ft.Text):
    """
    Calls the external updater.exe and closes the current app.
    """
    try:
        if dev_mode:
            raise Exception("It is not possible to apply an update to a development version.")
        
        logging.info(f"Copying 'updater.exe' to temporary storage: {os.path.abspath("assets/updater/updater.exe")}")
        shutil.copy(os.path.abspath("assets/updater/updater.exe"), FLET_APP_STORAGE_TEMP)
        
        executable_path = os.path.join(get_app_path(), "pyz_launcher.exe")
        updater_exe = os.path.join(FLET_APP_STORAGE_TEMP, "updater.exe")

        logging.info(f"Executable path: {executable_path!r}")
        logging.info(f"Updater path: {updater_exe!r}")
        logging.info(f"Zip path: {zip_path!r}")

        if not os.path.exists(updater_exe):
            logging.error("Error: updater.exe not found.")
            return

        logging.info(f"Launching {updater_exe}...")
        __update_status_safe(page, status_text, f"Launching {updater_exe}...")

        # ARGUMENTS: [Updater Path, Zip Path, Main App Path]
        subprocess.Popen([updater_exe, zip_path, executable_path])

        # Close this app immediately so the updater can overwrite files
        page.window.close()
        sys.exit(0)

    except Exception as e:
        error_msg = f"Failed to launch updater: {e}"
        __update_status_safe(page, status_text, error_msg)
        logging.error(error_msg)
# This file is part of PYZ-LAUNCHER-FOR-MINECRAFT (https://github.com/ZadkielAvendano/PyZ-Launcher-for-Minecraft)
# Copyright (c) 2025 Zadkiel Avendano and collaborators
# License-Identifier: MIT License

import flet as ft
import minecraft_launcher_lib as mll
from modules.app_config import *
from modules.refresh_handler import *
import subprocess
import logging
import datetime
import time

# Create a directory for logs if it doesn't exist
if not os.path.exists("logs"):
    os.makedirs("logs")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(f"logs/launcher-{datetime.date.today()}.log"), # Save the logs to a file
        logging.StreamHandler() # It also shows them in the console
    ]
)

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


# ----- Launcher Logic -----


def launch_game(home_view, version_id: str, status_text_control: ft.Text, buttons_to_disable: list, play_button: ft.Button):
    """
    Starts Minecraft using the specified version and user settings.
    """
    try:
        __set_controls_enabled_safe(home_view.page, buttons_to_disable, False)
        
        # Launch options
        options = {
            "username": app_settings.get_setting(AppData.USERNAME),
            "uuid": app_settings.get_setting(AppData.UUID), # UUID offline
            "token": "", # offline
            # "executablePath": "/path/to/your/java/bin/java" # Java
            "jvmArguments": app_settings.get_setting(AppData.JVM_ARGUMENTS) # JVM
        }

        # Get the launch command
        __update_status_safe(home_view.page, status_text_control, "Generating launch command...")
        minecraft_command = mll.command.get_minecraft_command(version=version_id,
                                                              minecraft_directory=app_settings.return_mc_directory(),
                                                              options=options)
        
        __update_status_safe(home_view.page, status_text_control, "Starting Minecraft...")
        play_button.text = "Starting Minecraft..."
        play_button.update()
        
        # Command
        process = subprocess.Popen(minecraft_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding="utf-8", creationflags=subprocess.CREATE_NO_WINDOW)
        __update_status_safe(home_view.page, status_text_control, f"Minecraft ({app_settings.get_setting(AppData.USERNAME)} - {version_id}) Started. PID: {process.pid}")
        play_button.text = "Running Minecraft..."
        play_button.update()
        
        # Wait
        stdout, stderr = process.communicate()

        # --- EXIT CODE REVIEW AND LOG-IN ---
        if process.returncode != 0:
            # If the exit code is not 0, something went wrong.
            error_message = f"Minecraft closed with an error (code: {process.returncode})."
            logging.error(error_message)
            logging.error("--- ERROR DETAILS (stderr) ---")
            logging.error(stderr if stderr else "Nothing reported on stderr.")
            logging.error("--- STANDARD OUTPUT (stdout) ---")
            logging.error(stdout if stdout else "Nothing reported on stdout.")
            
            # Update the UI
            home_view.error_launch_game(f"{stderr}\n{stdout}")
            __update_status_safe(home_view.page, status_text_control, f"Error launching Minecraft. Check logs/launcher-{datetime.date.today()}.log for details.")
        else:
            # The game closed successfully
            __update_status_safe(home_view.page, status_text_control, "Minecraft closed successfully.")
            logging.info("Minecraft closed successfully.")

    except Exception as e:
        __update_status_safe(home_view.page, status_text_control, f"Error: {str(e)}")
    finally:
        __set_controls_enabled_safe(home_view.page, buttons_to_disable, True)
        refresh()



current_max = 0

def __set_progress(page: ft.Page, progress: int, progress_bar: ft.ProgressBar, progress_text: ft.Text):
    if current_max != 0:
        progress_bar.value = progress / current_max
        progress_bar.update()
        __update_status_safe(page, progress_text, f"{progress}/{current_max}")

def __set_max(new_max: int):
    global current_max
    current_max = new_max



def install_version(page: ft.Page, version_id: str, buttons_to_disable: list, progress_window: ft.AlertDialog,
                    progress_bar: ft.ProgressBar, status_text: ft.Text, progress_text: ft.Text):
    """
    Installs the specified Minecraft version while updating the progress bar and status messages.
    """
    try:
        __set_controls_enabled_safe(page, buttons_to_disable, False)
        __update_status_safe(page, status_text, f"Checking version: {version_id}...")

        callback={
            "setStatus": lambda status: __update_status_safe(page, status_text, f"{status}"),
            "setProgress": lambda progress: __set_progress(page, progress, progress_bar, progress_text),
            "setMax": __set_max
            }

        mll.install.install_minecraft_version(versionid=version_id, minecraft_directory=app_settings.return_mc_directory(), callback=callback)
        __update_status_safe(page, status_text, f"Version ({version_id}) installed!")

    except Exception as e:
        __update_status_safe(page, status_text, f"Error: {str(e)}")
    finally:
        time.sleep(3)
        page.close(progress_window)
        __set_controls_enabled_safe(page, buttons_to_disable, True)
        refresh()



def get_versions() -> dict:
    """Returns a dict of all Minecraft versions (installed, release, snapshot, old_beta, old_alpha)"""

    versions = mll.utils.get_version_list()
    installed = mll.utils.get_installed_versions(app_settings.return_mc_directory())
    return {
        "installed": installed,
        "release": [v["id"] for v in versions if v["type"] == "release"],
        "snapshot": [v["id"] for v in versions if v["type"] == "snapshot"],
        "old_beta": [v["id"] for v in versions if v["type"] == "old_beta"],
        "old_alpha": [v["id"] for v in versions if v["type"] == "old_alpha"]
    }
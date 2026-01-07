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
        options: mll.types.MinecraftOptions = {
            "username": app_settings.get_setting(AppData.USERNAME),
            "uuid": app_settings.get_setting(AppData.UUID), # UUID offline
            "token": "", # offline
            "jvmArguments": app_settings.get_setting(AppData.JVM_ARGUMENTS), # JVM Arguments
            # Launcher info
            "launcherName": app_name,
            "launcherVersion": app_version,
        }

        if app_settings.get_setting(AppData.EXECUTABLE_PATH) != "":
            options["executablePath"] = app_settings.get_setting(AppData.EXECUTABLE_PATH)

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
        home_view.error_launch_game(f"Error: {str(e)}")
        __update_status_safe(home_view.page, status_text_control, f"Error: {str(e)}")
    finally:
        __set_controls_enabled_safe(home_view.page, buttons_to_disable, True)
        refresh()



current_max = 0

def __set_progress(page: ft.Page, progress: int, progress_bar: ft.ProgressBar, progress_text: ft.Text):
    if current_max != 0:
        progress_bar.value = progress / current_max
        progress_bar.update()
        page.window.progress_bar = progress / current_max
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
        
        check = check_version(version_id)

        if check != "not_compatible" and type(check) != str:

            if check[0] == "vanilla":
                # Vanilla installer
                print(f"Installing vanilla version...\nVersion: {version_id}")
                mll.install.install_minecraft_version(version=version_id, minecraft_directory=app_settings.return_mc_directory(), callback=callback)
                __update_status_safe(page, status_text, f"Version ({version_id}) installed!")
                page.window.progress_bar = 0

            elif check[0] == "mod_loader":
                # Mod loader installer
                print(f"Installing mod loader version...\nVersion: {version_id} Mod Loader: {check[1]} Loader Version: {check[2]} Minecraft Version: {check[3]}")
                mod_loader = mll.mod_loader.get_mod_loader(check[1])
                mod_loader.install(minecraft_version=check[3], minecraft_directory=app_settings.return_mc_directory(), loader_version=check[2], callback=callback,
                                   java=app_settings.get_setting(AppData.EXECUTABLE_PATH) if app_settings.get_setting(AppData.EXECUTABLE_PATH) != "" else None)
                __update_status_safe(page, status_text, f"Version ({version_id}) with {check[1]} installed!")
                page.window.progress_bar = 0

            else:
                raise Exception("This version is not compatible with the launcher or mod loaders installed.")
        else:
            raise Exception("This version is not compatible with the launcher or mod loaders installed.")

    except Exception as e:
        __update_status_safe(page, status_text, f"Error: {str(e)}")
    finally:
        time.sleep(3)
        page.close(progress_window)
        __set_controls_enabled_safe(page, buttons_to_disable, True)
        refresh()



def is_version_installed(version_id: str) -> bool:
    """Checks if the specified Minecraft version is installed."""
    if version_id == "latest-release":
        version_id = mll.utils.get_latest_version()["release"]
    elif version_id == "latest-snapshot":
        version_id = mll.utils.get_latest_version()["snapshot"]
    installed_list_id = [v["id"] for v in get_versions()["installed"]]
    if not mll.utils.is_minecraft_installed(app_settings.return_mc_directory()) or version_id not in installed_list_id:
        return False
    else:
        return True
    


def check_version(version: str) -> tuple:
    """
    Returns:\n
    "vanilla" -> Vanilla version\n
    "mod_loader" -> Mod loader version\n
    "not_compatible" -> Not compatible version
    """
    if mll.utils.is_vanilla_version(version):
        return "vanilla", version
    else:
        if any(elem in version for elem in ["fabric", "forge", "quilt"]):
                    if "fabric-loader" in version:
                        loader = "fabric"
                    elif "quilt-loader" in version:    
                        loader = "quilt"
                    elif "-forge-" in version:
                        loader = "forge"

                    version_items = version.split("-")
                    print(version_items)
                    if loader == "fabric" or loader == "quilt":
                        mc_version = version_items[3]
                        mod_loader_version = version_items[2]
                    elif loader == "forge":
                        mc_version = version_items[0]
                        mod_loader_version = version_items[2]

                    mod_loader = mll.mod_loader.get_mod_loader(loader)
                    if mc_version and mod_loader.is_minecraft_version_supported(mc_version):
                        return "mod_loader", loader, mod_loader_version, mc_version
        else:
            return "not_compatible"



def get_versions(version_type: str = "vanilla") -> dict:
    """Returns a dict of all Minecraft versions (installed, release, snapshot, old_beta, old_alpha)"""
    # Mod loaders
    if version_type in mll.mod_loader.list_mod_loader():
        mod_loader = mll.mod_loader.get_mod_loader(version_type)
        if mod_loader:
            minecraft_versions = mod_loader.get_minecraft_versions(stable_only=True)
            installed = mll.utils.get_installed_versions(app_settings.return_mc_directory())
            return {
                "installed": installed,
                "version": minecraft_versions
            }
        else:
            return {
                "installed": [],
                "version": []
            }
    # Vanilla versions
    else:
        versions = mll.utils.get_version_list()
        installed = mll.utils.get_installed_versions(app_settings.return_mc_directory())
        return {
            "installed": installed,
            "release": [v["id"] for v in versions if v["type"] == "release"],
            "snapshot": [v["id"] for v in versions if v["type"] == "snapshot"],
            "old_beta": [v["id"] for v in versions if v["type"] == "old_beta"],
            "old_alpha": [v["id"] for v in versions if v["type"] == "old_alpha"]
    }
import flet as ft
import minecraft_launcher_lib as mll
from modules.app_config import *
import subprocess
import time

def update_status_safe(page: ft.Page, control, message):
    """Update a Flet control safely from a thread."""
    if page and control:
        control.value = message
        try:
            page.update()
        except Exception:
            pass

def set_controls_enabled_safe(page: ft.Page, controls, enabled):
    """Safely enable or disable Flet controls."""
    if page:
        for control in controls:
            control.disabled = not enabled
        try:
            page.update()
        except Exception:
            pass


# ----- Launcher Logic -----


def launch_game(page: ft.Page, version_id: str, status_text_control: ft.Text, buttons_to_disable: list, play_button: ft.Button, refresh):
    try:
        set_controls_enabled_safe(page, buttons_to_disable, False)
        
        # Launch options
        options = {
            "username": app_settings.get_setting(AppData.USERNAME),
            "uuid": app_settings.get_setting(AppData.UUID), # UUID offline
            "token": "", # offline
            # "executablePath": "/path/to/your/java/bin/java" # Java
            "jvmArguments": app_settings.get_setting(AppData.JVM_ARGUMENTS) # JVM
        }

        # Get the launch command
        update_status_safe(page, status_text_control, "Generating launch command...")
        minecraft_command = mll.command.get_minecraft_command(version=version_id,
                                                              minecraft_directory=app_settings.return_mc_directory(),
                                                              options=options)
        
        update_status_safe(page, status_text_control, "Starting Minecraft...")
        play_button.text = "Starting Minecraft..."
        play_button.update()
        
        # Ejecutar el comando
        process = subprocess.Popen(minecraft_command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, creationflags=subprocess.CREATE_NO_WINDOW)
        update_status_safe(page, status_text_control, f"Minecraft ({app_settings.get_setting(AppData.USERNAME)} - {version_id}) Started. PID: {process.pid}")
        play_button.text = "Running Minecraft..."
        play_button.update()
        
        # Opcional: Esperar a que el proceso termine y luego reactivar botones
        process.wait()
        update_status_safe(page, status_text_control, "Minecraft closed.")

    except Exception as e:
        update_status_safe(page, status_text_control, f"Error: {str(e)}")
    finally:
        set_controls_enabled_safe(page, buttons_to_disable, True)
        refresh()



current_max = 0

def set_progress(progress: int, progress_bar: ft.ProgressBar):
    if current_max != 0:
        progress_bar.value = progress / current_max
        progress_bar.update()
        print(f"{progress}/{current_max}")

def set_max(new_max: int):
    global current_max
    current_max = new_max



def install_version(page: ft.Page, version_id: str, buttons_to_disable: list, progress_window: ft.AlertDialog, progress_bar: ft.ProgressBar, status_text: ft.Text, refresh):
    try:
        set_controls_enabled_safe(page, buttons_to_disable, False)
        update_status_safe(page, status_text, f"Checking version: {version_id}...")

        callback={
            "setStatus": lambda status: update_status_safe(page, status_text, f"{status}"),
            "setProgress": lambda progress: set_progress(progress, progress_bar),
            "setMax": set_max
            }

        mll.install.install_minecraft_version(versionid=version_id, minecraft_directory=app_settings.return_mc_directory(), callback=callback)
        update_status_safe(page, status_text, f"Version ({version_id}) installed!")

    except Exception as e:
        update_status_safe(page, status_text, f"Error: {str(e)}")
    finally:
        time.sleep(3)
        page.close(progress_window)
        set_controls_enabled_safe(page, buttons_to_disable, True)
        refresh()



def get_versions() -> dict:
    versions = mll.utils.get_version_list()
    installed = mll.utils.get_installed_versions(app_settings.return_mc_directory())
    return {
        "installed": [v["id"] for v in installed],
        "releases": [v["id"] for v in versions if v["type"] == "release"],
        "snapshots": [v["id"] for v in versions if v["type"] == "snapshot"]
    }
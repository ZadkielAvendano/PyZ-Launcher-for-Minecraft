# This file is part of PYZ-LAUNCHER-FOR-MINECRAFT (https://github.com/ZadkielAvendano/PyZ-Launcher-for-Minecraft)
# Copyright (c) 2026 Zadkiel Avendano and collaborators
# License-Identifier: MIT License

from typing import Callable
from modules.app_config import *

# List of registered event functions that should be executed upon refresh
refresh_list: list[Callable[[], None]] = []

def refresh(e: ft.Control = None):
    """
    Executes all registered refresh events and updates the UI.

    This function iterates through the `refresh_list`, executing each registered event.
    If the list is empty, it logs that no events have been recorded.

    Parameters:
        e (ft.Control, optional): UI control triggering the refresh event. Defaults to None.
    """
    if refresh_list:
        try:
            for event in refresh_list:
                event()
            app_settings.page.update()
            print("Refresh!")
        except Exception as ex:
            print(f"Error: {ex}")
    else:
        print("No events recorded.")
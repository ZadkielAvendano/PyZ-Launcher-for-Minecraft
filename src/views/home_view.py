# This file is part of PYZ-LAUNCHER-FOR-MINECRAFT (https://github.com/ZadkielAvendano/PyZ-Launcher-for-Minecraft)
# Copyright (c) 2025 Zadkiel Avendano and collaborators
# License-Identifier: MIT License

import flet as ft
from modules.app_config import *
from modules.launcher import *
from modules.refresh_handler import *
from modules.utils import *
from widgets.app import WindowTittleBar
import minecraft_launcher_lib as mll
import threading
import datetime
import re
import os


## ----- FLET UI -----


class HomeView():
    def __init__(self, page: ft.Page, launcher_profiles_view):
        self.page = page

        self.installed_options: list[ft.DropdownOption] = []
        self.versions_options: list[ft.DropdownOption] = []

        self.username_text = ft.Text(
            value=app_settings.get_setting(AppData.USERNAME),
            weight=ft.FontWeight.BOLD,
            color=ft.Colors.WHITE,
            size=20
            )

        self.username_input = ft.TextField(
            label="Username (Offline)",
            width=300,
            border_color=ft.Colors.WHITE24,
            color=ft.Colors.WHITE,
            focused_bgcolor="#4A4A4A",
            focused_border_color=ft.Colors.PRIMARY,
            value=app_settings.get_setting(AppData.USERNAME),
            on_submit=self.set_username
        )

        self.minecraft_directory_input = ft.TextField(
            label="Minecraft directory",
            hint_text="Empty to use the default directory",
            width=350,
            border_color=ft.Colors.WHITE24,
            color=ft.Colors.WHITE,
            focused_bgcolor="#4A4A4A",
            focused_border_color=ft.Colors.PRIMARY,
            value=app_settings.return_mc_directory()
        )

        self.installed_dropdown = ft.Dropdown(
            label="Installed versions",
            hint_text="Choose a version",
            options=self.installed_options,
            width=200,
            bgcolor="#3C3C3C",
            border_color=ft.Colors.WHITE24,
            color=ft.Colors.WHITE,
            on_change=self.refresh_play_button
        )

        self.maximum_ram_slider = ft.Slider(
            value=int(re.search(r"\d+", app_settings.get_setting(AppData.JVM_ARGUMENTS)[0]).group()),
            label="{value} GB",
            min=1, 
            max=16,
            divisions=15,
            width=350
            )

        self.play_button = ft.FilledButton(
            text="PLAY",
            on_click=self.ui_launch_game,
            width=200,
            height=50,
            style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=5)),
            tooltip="Install and play Minecraft"
        )

        self.versions_button = ft.IconButton(
            icon=ft.Icons.DOWNLOAD,
            icon_size=25,
            icon_color=ft.Colors.WHITE,
            tooltip="Install versions",
            on_click=lambda e: page.go("/launcher-profiles")
        )

        self.settings_button = ft.IconButton(
            icon=ft.Icons.SETTINGS,
            icon_size=25,
            icon_color=ft.Colors.WHITE,
            tooltip="Settings",
            on_click=lambda e: page.open(self.settings_window)
        )

        self.username_button = ft.IconButton(
            icon=ft.Icons.MANAGE_ACCOUNTS,
            icon_size=25,
            icon_color=ft.Colors.WHITE,
            tooltip="Manage username",
            on_click=lambda e: page.open(self.username_window)
        )

        self.status_text = ft.Text("Status: Ready", size=12, color=ft.Colors.AMBER, max_lines=3, overflow=ft.TextOverflow.ELLIPSIS)

        self.progress_text = ft.Text("", size=12, color=ft.Colors.AMBER, max_lines=3, overflow=ft.TextOverflow.ELLIPSIS)
        
        self.info_minecraft_dir = ft.Text(
            f"Minecraft directory: {app_settings.return_mc_directory()}",
            size=10,
            color=ft.Colors.GREY_500,
            italic=True
        )

        self.progress_bar = ft.ProgressBar(value=0, width=400, border_radius=5)

        self.progress_window = ft.AlertDialog(
            modal=True,
            title="Installing...",
            bgcolor="#3C3C3C",
            scrollable=True,
            content=ft.Column(
                expand=False,
                controls=[
                    self.progress_bar,
                    ft.Row(
                        controls=[
                            self.status_text,
                            ft.Container(expand=True),
                            self.progress_text
                        ]
                    )
                ]
            )
        )

        self.settings_window = ft.AlertDialog(
            modal=True,
            title="Settings",
            bgcolor="#3C3C3C",
            scrollable=True,
            content=ft.Column(
                expand=False,
                controls=[
                    self.minecraft_directory_input,
                    ft.Text("Maximum memory (RAM):", size=15, weight=ft.FontWeight.BOLD),
                    self.maximum_ram_slider,
                    # ft.Text("Java executable:", size=15, weight=ft.FontWeight.BOLD),
                    # ft.Text("JVM arguments:", size=15, weight=ft.FontWeight.BOLD)
                ]
            ),
            actions=[
                ft.TextButton("Apply settings", on_click=self.set_settings),
                ft.TextButton("Close", on_click=lambda e: page.close(self.settings_window))
                ]
        )

        self.username_window = ft.AlertDialog(
            modal=True,
            title="Username",
            bgcolor="#3C3C3C",
            scrollable=True,
            content=ft.Column(
                expand=False,
                controls=[
                    self.username_input
                ]
            ),
            actions=[
                ft.TextButton("Apply", on_click=self.set_username),
                ft.TextButton("Close", on_click=lambda e: page.close(self.username_window))
                ]
        )

        self.error_game_window = ft.AlertDialog(
                modal=True,
                title="Error in game execution",
                bgcolor="#3C3C3C",
                scrollable=True,
                content=ft.Column(
                    expand=False,
                    controls=[
                        ft.Text(value="-- Error Message --")
                    ]
                ),
                actions=[
                    ft.TextButton("Repair version", visible=True, on_click=self.repair_version),
                    ft.TextButton("View logs", on_click=lambda e: open_file(f"logs/launcher-{datetime.date.today()}.log")),
                    ft.TextButton("Close", on_click=lambda e: self.page.close(self.error_game_window))
                    ]
            )


        # ---- View ----


        self.view = ft.View(
            "/",
            [ft.Text(app_name.upper(), size=30, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE)],
            padding=10,
            spacing=20,
            vertical_alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            appbar=WindowTittleBar(self.page),
            bottom_appbar=ft.BottomAppBar(
                bgcolor="#3C3C3C",
                height=100,
                content=ft.Column(
                    controls=[
                        ft.Row(
                            controls=[
                                self.play_button,
                                self.installed_dropdown,
                                self.versions_button,
                                self.settings_button,
                                ft.Container(expand=True),
                                self.username_text,
                                self.username_button
                            ]
                        ),
                        ft.Row(
                            controls=[
                                self.status_text,
                                ft.Container(expand=True),
                                self.info_minecraft_dir
                            ]
                        )
                    ]
                ),
            ),
            bgcolor=ft.Colors.TRANSPARENT,
            decoration=ft.BoxDecoration(
                image=ft.DecorationImage(
                    src="/background.png",
                    fit=ft.ImageFit.COVER,
                    opacity=0.25
                )
            ),
            scroll=False
        )

    

    def refresh_ui(self, e: ft.Control = None):
        versions = get_versions()
        last_played = app_settings.get_setting(AppData.LAST_PLAYED)

        # Retrieve installed and available versions
        if mll.vanilla_launcher.do_vanilla_launcher_profiles_exists(app_settings.return_mc_directory()):
            self.installed_options = []
            for profile in mll.vanilla_launcher.load_vanilla_launcher_profiles(app_settings.return_mc_directory()):
                version_type = profile["versionType"]
                if version_type in {"latest-release", "latest-snapshot"}:
                    self.installed_options.append(ft.DropdownOption(key=version_type, text=version_type.replace("-", " ").capitalize(), data=profile))
                else:
                    self.installed_options.append(ft.DropdownOption(key=profile["version"], text=profile["name"], data=profile))
        try:
            # Configure installed versions dropdown
            self.installed_dropdown.options = self.installed_options

            if last_played and last_played in {"latest-release", "latest-snapshot"}:
                self.installed_dropdown.value = last_played
            elif last_played and mll.vanilla_launcher.do_vanilla_launcher_profiles_exists(app_settings.return_mc_directory()):
                for profile in mll.vanilla_launcher.load_vanilla_launcher_profiles(app_settings.return_mc_directory()):
                    if profile["version"] == last_played:
                        self.installed_dropdown.value = last_played
                        break
            else:
                self.installed_dropdown.value = "latest-release"
                if last_played:
                    app_settings.save_settings(AppData.LAST_PLAYED, "latest-release")

        except Exception as e:
            print(f"Error: {e}")

        # Set play button text based on Minecraft installation status
        self.refresh_play_button()

        # Load user information
        self.username_input.value = app_settings.get_setting(AppData.USERNAME)
        self.username_text.value = app_settings.get_setting(AppData.USERNAME)

        # Display Minecraft directory path
        self.info_minecraft_dir.value = f"Minecraft directory: {app_settings.return_mc_directory()}"
        self.minecraft_directory_input.value = app_settings.return_mc_directory()

        # Configure maximum RAM slider from JVM arguments
        jvm_args = app_settings.get_setting(AppData.JVM_ARGUMENTS)
        self.maximum_ram_slider.value = int(re.search(r"\d+", jvm_args[0]).group())

    
    def refresh_play_button(self, e: ft.Control = None):
        if mll.utils.is_minecraft_installed(app_settings.return_mc_directory()):
            versions = [v["id"] for v in get_versions()["installed"]]
            if self.installed_dropdown.value == "latest-release":
                version = mll.utils.get_latest_version()["release"]
            elif self.installed_dropdown.value == "latest-snapshot":
                version = mll.utils.get_latest_version()["snapshot"]
            else:
                version = self.installed_dropdown.value
            self.play_button.text = "PLAY" if version in versions else "INSTALL"
        else:
            self.play_button.text = "INSTALL"
        self.play_button.update()


    def set_username(self, e: ft.Control = None):
        username: str = self.username_input.value
        if len(username) >= 3 and len(username) <= 16 and " " not in username:
            app_settings.save_settings(AppData.USERNAME, username)
            self.username_input.error_text = None
            self.page.close(self.username_window)
            refresh()
        else:
            self.username_input.error_text = "Enter a valid username"
            self.page.update()


    def set_settings(self, e: ft.Control = None):
        minecraft_directory: str = self.minecraft_directory_input.value
        maximum_ram: int = round(self.maximum_ram_slider.value)
        if not os.path.exists(minecraft_directory) and minecraft_directory != "":
            self.minecraft_directory_input.error_text = "Enter a valid directory"
            self.page.update()
            return
        else:
            app_settings.save_settings(AppData.MC_DIRECTORY, minecraft_directory)
            app_settings.save_settings(AppData.JVM_ARGUMENTS, [f"-Xmx{maximum_ram}G", f"-Xms{maximum_ram}G"])
            self.minecraft_directory_input.error_text = None
            self.page.close(self.settings_window)
            refresh()
        

    
    def ui_launch_game(self, e: ft.Control = None):
        selected_version = self.return_current_version(save_version=True)
        installed_list_id = [v["id"] for v in get_versions()["installed"]]

        if selected_version not in installed_list_id:
            self.ui_install_game(None, selected_version)
            return
        
        # Run in a thread to avoid blocking the Flet UI
        buttons_to_disable = [self.play_button, self.installed_dropdown, self.versions_button, self.settings_button, self.username_button]
        thread = threading.Thread(target=launch_game, args=(self, selected_version, self.status_text, buttons_to_disable, self.play_button))
        thread.daemon = True
        thread.start()

    
    def ui_install_game(self, e: ft.Control = None, selected_version: str = None):
        if not selected_version:
            self.status_text.value = "Please select a version."
            return
        self.page.open(self.progress_window)
        buttons_to_disable = [self.play_button, self.installed_dropdown, self.versions_button, self.settings_button, self.username_button]
        thread = threading.Thread(target=install_version, args=(self.page, selected_version, buttons_to_disable, self.progress_window, self.progress_bar,
                                                                self.status_text, self.progress_text))
        thread.daemon = True
        thread.start()

    def error_launch_game(self, error_message: str):
        selected_version = self.return_current_version()
        self.error_game_window.actions[0].visible = True if mll.utils.is_vanilla_version(selected_version) else False
        self.error_game_window.content.controls = [ft.Text(value=error_message)]
        self.page.open(self.error_game_window)

    def repair_version(self, e):
        selected_version = self.return_current_version()
        if mll.utils.is_vanilla_version(selected_version):
            self.ui_install_game(e, selected_version)
        self.page.close(self.error_game_window)

    def return_current_version(self, save_version: bool = False) -> str:
        selected_version = self.installed_dropdown.value

        if not selected_version:
            self.status_text.value = "Please select a version."
            return

        if selected_version == "latest-release":
            selected_version = mll.utils.get_latest_version()["release"]
            app_settings.save_settings(AppData.LAST_PLAYED, "latest-release") if save_version else None
        elif selected_version == "latest-snapshot":
            selected_version = mll.utils.get_latest_version()["snapshot"]
            app_settings.save_settings(AppData.LAST_PLAYED, "latest-snapshot") if save_version else None
        else:
            # Save the last played version
            app_settings.save_settings(AppData.LAST_PLAYED, selected_version) if save_version else None
        
        return selected_version
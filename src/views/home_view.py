# This file is part of PYZ-LAUNCHER-FOR-MINECRAFT (https://github.com/ZadkielAvendano/PyZ-Launcher-for-Minecraft)
# Copyright (c) 2026 Zadkiel Avendano and collaborators
# License-Identifier: MIT License

import flet as ft
from modules.app_config import *
from modules.launcher import *
from modules.refresh_handler import *
from modules.utils import system_ram, open_file, get_app_path
from modules.updater import has_update, download_launcher_update
from widgets.app import WindowTittleBar
from widgets.RotatingText import HighlightRotatingText
import minecraft_launcher_lib as mll
import threading
import datetime
import re
import os


## ----- FLET UI -----


class HomeView():
    def __init__(self, page: ft.Page, launcher_profiles_view: ft.View):
        self.page = page
        self.ready = False

        self.installed_options: list[ft.DropdownOption] = []
        self.versions_options: list[ft.DropdownOption] = []

        self.username_text = ft.Text(
            value=app_settings.get_setting(AppData.USERNAME),
            weight=ft.FontWeight.BOLD,
            color=ft.Colors.WHITE,
            size=20
            )

        self.maximum_ram_text = ft.Text("Maximum memory (RAM):", size=15, weight=ft.FontWeight.BOLD)

        self.system_ram_text = ft.Text("System RAM: / Used RAM: / Available RAM:", size=12, italic=True, color=ft.Colors.GREY_500,)

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

        self.java_directory_input = ft.TextField(
            label="Java directory",
            hint_text="Empty to use the default directory",
            width=350,
            border_color=ft.Colors.WHITE24,
            color=ft.Colors.WHITE,
            focused_bgcolor="#4A4A4A",
            focused_border_color=ft.Colors.PRIMARY
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
            max=system_ram()["total"], # Max RAM in GB
            divisions=system_ram()["total"] - 1,
            width=350,
            on_change=self.refresh_ram_slider
        )

        self.play_button = ft.FilledButton(
            text="PLAY",
            on_click=self.ui_launch_game,
            width=200,
            height=50,
            style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=5)),
            tooltip="Install and play Minecraft"
        )

        self.check_for_updates_button = ft.FilledButton(
            text="Check for updates",
            on_click=self.check_for_updates,
            width=300,
            height=50,
            style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=5)),
            tooltip="Check for updates",
        )

        self.update_launcher_button = ft.FilledButton(
            text="Download Update",
            width=300,
            height=50,
            style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=5)),
            on_click=self.ui_update_launcher,
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

        self.check_on_startup = ft.Switch(
            label="Check for updates on startup: ",
            label_position=ft.LabelPosition.LEFT,
            label_style=ft.TextStyle(size=15, weight=ft.FontWeight.BOLD),
            value=app_settings.get_setting(AppData.CHECK_UPDATES_ON_STARTUP),
            on_change=lambda e: app_settings.save_settings(AppData.CHECK_UPDATES_ON_STARTUP, e.control.value)
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
            modal=False,
            title="Settings",
            bgcolor="#3C3C3C",
            scrollable=True,
            content=ft.Tabs(
                selected_index=0,
                animation_duration=0,
                height=360,
                width=400,
                expand=True,
                animate_size=ft.Animation(duration=300, curve=ft.AnimationCurve.EASE_OUT),
                on_change=self.refresh_settings_tab_window,
                tabs=[
                    ft.Tab(
                        text="Game",
                        content=ft.Column(
                            expand=True,
                            scroll=ft.ScrollMode.ADAPTIVE,
                            horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
                            controls=[
                                ft.Container(height=5),
                                ft.Text("Minecraft Directory:", size=15, weight=ft.FontWeight.BOLD),
                                self.minecraft_directory_input,
                                ft.Text("Java executable:", size=15, weight=ft.FontWeight.BOLD),
                                self.java_directory_input,
                                self.maximum_ram_text,
                                self.system_ram_text,
                                self.maximum_ram_slider,
                                # ft.Text("JVM arguments:", size=15, weight=ft.FontWeight.BOLD)
                            ]
                        )
                    ),
                    ft.Tab(
                        text="Launcher",
                        content=ft.Column(
                            expand=False,
                            scroll=ft.ScrollMode.ADAPTIVE,
                            horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
                            controls=[
                                ft.Container(height=10),
                                self.check_for_updates_button,
                                self.check_on_startup,
                                ft.Divider(),
                                ft.Text(f"App Name: {app_name}", size=12),
                                ft.Text(f"App Version: {app_version}", size=12),
                                ft.Text("Environment: " + ("Development" if dev_mode else "Production"), size=12),
                                ft.Text(f"App Path: {get_app_path()}", selectable=True, size=12, italic=True, color=ft.Colors.GREY_500),
                            ]
                        )
                    )
                ]
            ),
            actions=[
                ft.TextButton("Apply settings", on_click=self.set_settings),
                ft.TextButton("Close", on_click=self.close_settings_window)
            ],
            on_dismiss=self.close_settings_window
        )

        self.username_window = ft.AlertDialog(
            modal=False,
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
                ft.TextButton("Close", on_click=self.close_username_window)
            ],
            on_dismiss=self.close_username_window
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
        
        self.updater_window = ft.AlertDialog(
                modal=True,
                title="Update Available",
                bgcolor="#3C3C3C",
                scrollable=True,
                content=ft.Column(
                    expand=False,
                    controls=[
                        self.update_launcher_button,
                        ft.Text(value="Update available: -- Version --"),
                        ft.Divider(),
                        self.check_on_startup
                    ]
                ),
                actions=[
                    ft.TextButton("Close", on_click=lambda e: self.page.close(self.updater_window))
                ]
            )


        # -------- VIEW --------


        self.view = ft.View(
            route="/",
            controls=[
                ft.Text(app_name.upper(), size=30, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                HighlightRotatingText(
                    static_text="for Minecraft",
                    phrases=["Vanilla", "Fabric", "Forge", "Quilt"],
                    bold=True,
                    box_color=ft.Colors.GREEN_ACCENT_700,
                    color=ft.Colors.WHITE,
                    direction="bottom",
                    loop=True,
                    static_style=ft.TextStyle(
                        color=ft.Colors.WHITE,
                        size=30,
                        weight="bold"
                    ),
                    width_factor=22,
                    interval=2
                )
                ],
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


    def close_username_window(self, e: ft.Control = None):
        self.username_input.value = app_settings.get_setting(AppData.USERNAME)
        self.username_input.error_text = None
        self.page.close(self.username_window)

    def close_settings_window(self, e: ft.Control = None):
        self.minecraft_directory_input.value = app_settings.return_mc_directory()
        self.java_directory_input.value = app_settings.get_setting(AppData.EXECUTABLE_PATH)
        self.maximum_ram_slider.value = int(re.search(r"\d+", app_settings.get_setting(AppData.JVM_ARGUMENTS)[0]).group())
        self.minecraft_directory_input.error_text = None
        self.java_directory_input.error_text = None
        self.settings_window.content.selected_index = 0
        self.page.close(self.settings_window)
        self.refresh_settings_tab_window()
        self.refresh_ram_slider()



    def refresh_ui(self, e: ft.Control = None):
        versions = get_versions()
        last_played = app_settings.get_setting(AppData.LAST_PLAYED)
        launcher_profiles_exists = mll.vanilla_launcher.do_vanilla_launcher_profiles_exists(app_settings.return_mc_directory())
        if launcher_profiles_exists:
            launcher_profiles = mll.vanilla_launcher.load_vanilla_launcher_profiles(app_settings.return_mc_directory())

        # Retrieve installed and available versions
        if launcher_profiles_exists:
            self.installed_options = []
            for profile in launcher_profiles:
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
            elif last_played and launcher_profiles_exists:
                count = len(launcher_profiles)
                for profile in launcher_profiles:
                    count -= 1
                    if profile["version"] == last_played:
                        self.installed_dropdown.value = last_played
                        break
                    elif count <= 0:
                        self.installed_dropdown.value = "latest-release"
                        if last_played:
                            app_settings.save_settings(AppData.LAST_PLAYED, "latest-release")
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

        # Display Java directory path
        self.java_directory_input.value = app_settings.get_setting(AppData.EXECUTABLE_PATH)

        # Configure maximum RAM slider from JVM arguments
        jvm_args = app_settings.get_setting(AppData.JVM_ARGUMENTS)
        self.maximum_ram_slider.value = int(re.search(r"\d+", jvm_args[0]).group())
        self.refresh_ram_slider()

        if self.ready == False:
            self.check_for_updates(open_dialog_window=False, on_startup=app_settings.get_setting(AppData.CHECK_UPDATES_ON_STARTUP))


    def refresh_ram_slider(self, e: ft.Control = None):
        total_ram = system_ram()["total"]
        used_ram = system_ram()["used"]
        available_ram = system_ram()["available"]
        self.maximum_ram_text.value = f"Maximum memory (RAM): {round(self.maximum_ram_slider.value)} GB"
        self.system_ram_text.value = f"System RAM: {total_ram} GB / Used RAM: {used_ram} GB / Available RAM: {available_ram} GB"
        if self.maximum_ram_slider.value > total_ram * 0.8:
            self.maximum_ram_slider.active_color = ft.Colors.ERROR
        elif self.maximum_ram_slider.value + used_ram > total_ram:
            self.maximum_ram_slider.active_color = ft.Colors.YELLOW_200
        else:
            self.maximum_ram_slider.active_color = ft.Colors.PRIMARY
        self.page.update()


    def refresh_settings_tab_window(self, e: ft.Control = None):
        selected_index = self.settings_window.content.selected_index
        if selected_index == 0:
            self.settings_window.content.height = 360
        elif selected_index == 1:
            self.settings_window.content.height = 320
        self.page.update()


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
        java_directory: str = self.java_directory_input.value
        maximum_ram: int = round(self.maximum_ram_slider.value)
        if not os.path.exists(minecraft_directory) and minecraft_directory != "":
            self.minecraft_directory_input.error_text = "Enter a valid directory"
            self.page.update()
            return
        elif not os.path.exists(java_directory) and java_directory != "":
            self.java_directory_input.error_text = "Enter a valid directory"
            self.page.update()
            return
        else:
            app_settings.save_settings(AppData.MC_DIRECTORY, minecraft_directory)
            app_settings.save_settings(AppData.EXECUTABLE_PATH, java_directory)
            app_settings.save_settings(AppData.JVM_ARGUMENTS, [f"-Xmx{maximum_ram}G", f"-Xms{maximum_ram}G"])
            self.minecraft_directory_input.error_text = None
            self.java_directory_input.error_text = None
            self.page.close(self.settings_window)
            refresh()
        

    
    def ui_launch_game(self, e: ft.Control = None):
        selected_version = self.return_current_version(save_version=True)
        if not is_version_installed(selected_version):
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
        self.progress_window.title = "Installing Version: " + selected_version
        self.page.open(self.progress_window)
        self.page.update()
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
        
        
        # --- pending: add modded version repair ---


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
    

    def ui_update_launcher(self, e: ft.Control = None):
        self.update_launcher_button.disabled = True
        self.page.update()
        latest_version = has_update()[1]
        self.update_launcher_button.disabled = False
        self.page.update()
        self.page.close(self.updater_window)
        if not has_update()[0] or not latest_version:
            self.status_text.value = "No updates available."
            self.page.update()
            return
        self.progress_window.title = "Updating to Version: " + latest_version
        self.page.open(self.progress_window)
        self.page.update()
        buttons_to_disable = [self.play_button, self.installed_dropdown, self.versions_button, self.settings_button, self.username_button]
        thread = threading.Thread(target=download_launcher_update, args=(latest_version, self.page, self.status_text, self.progress_bar, self.progress_text, buttons_to_disable, self.progress_window))
        thread.daemon = True
        thread.start()
    

    def check_for_updates(self, e: ft.Control = None, open_dialog_window: bool = True, on_startup: bool = False):
        tittle_bar: WindowTittleBar = self.view.appbar
        tittle_bar.remove_custom_actions()
        tittle_bar.add_custom_action(action=ft.ProgressRing(color=ft.Colors.GREEN_ACCENT_700, width=20, height=20))
        self.check_for_updates_button.disabled = True
        self.check_for_updates_button.content = ft.Row(alignment=ft.MainAxisAlignment.CENTER, controls=[
            ft.Text("Checking for updates...", size=15, weight=ft.FontWeight.BOLD),
            ft.ProgressRing(color=ft.Colors.ON_SURFACE, width=20, height=20)
            ])
        self.page.update()
        has_update_result = has_update()
        if has_update_result[0]:
            self.status_text.value = f"New Update available! Latest version: {has_update_result[1]}"
            tittle_bar.remove_custom_actions()
            tittle_bar.add_custom_action(
                action=ft.IconButton(
                            icon=ft.Icons.UPDATE,
                            tooltip="Update Available",
                            icon_color=ft.Colors.GREEN_ACCENT_700,
                            on_click=self.check_for_updates
                        )
            )
            if open_dialog_window or on_startup:
                self.page.open(self.updater_window)
                self.updater_window.title = "Update Available"
                self.updater_window.content.controls[1].value = f"Latest version: {has_update_result[1]}"
                self.updater_window.content.controls[0].visible = True
        elif open_dialog_window and not on_startup:
            self.page.open(self.updater_window)
            self.updater_window.title = "No Updates Available"
            self.updater_window.content.controls[1].value = "You are using the latest version."
            self.updater_window.content.controls[0].visible = False
            tittle_bar.remove_custom_actions()
        else:
            tittle_bar.remove_custom_actions()
        self.check_for_updates_button.disabled = False
        self.check_for_updates_button.content = None
        self.ready = True
        self.page.update()
import flet as ft
from modules.app_config import *
from modules.launcher import *
import minecraft_launcher_lib as mll
import threading
import re
import os


## ----- FLET UI -----


class HomeView():
    def __init__(self, page: ft.Page):
        self.page = page

        self.installed_options: list[ft.DropdownOption] = []
        self.releases_options: list[ft.DropdownOption] = []

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
            value=app_settings.get_setting(AppData.MC_DIRECTORY)
        )

        self.version_dropdown = ft.Dropdown(
            label="Game version",
            hint_text="Select a version",
            options=self.releases_options,
            width=300,
            bgcolor="#3C3C3C",
            border_color=ft.Colors.WHITE24,
            color=ft.Colors.WHITE
        )

        self.installed_dropdown = ft.Dropdown(
            label="Installed versions",
            hint_text="Choose a version",
            options=self.installed_options,
            width=200,
            bgcolor="#3C3C3C",
            border_color=ft.Colors.WHITE24,
            color=ft.Colors.WHITE
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

        self.install_button = ft.FilledButton(
            text="Install",
            on_click=self.ui_install_game,
            width=300,
            height=50,
            style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=5)),
            tooltip="Install Minecraft"
        )

        self.versions_button = ft.IconButton(
            icon=ft.Icons.DOWNLOAD,
            icon_size=25,
            icon_color=ft.Colors.WHITE,
            tooltip="Install versions",
            on_click=lambda e: page.open(self.installation_window)
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
        
        self.info_minecraft_dir = ft.Text(
            f"Minecraft directory: {app_settings.return_mc_directory()}",
            size=10,
            color=ft.Colors.GREY_500,
            italic=True
        )

        self.progress_bar = ft.ProgressBar(value=0, width=400)

        self.progress_window = ft.AlertDialog(
            modal=True,
            title="Installing...",
            bgcolor="#3C3C3C",
            scrollable=True,
            content=ft.Column(
                expand=False,
                controls=[
                    self.progress_bar,
                    self.status_text
                ]
            )
        )

        self.installation_window = ft.AlertDialog(
            modal=True,
            title="Install Minecraft version",
            bgcolor="#3C3C3C",
            scrollable=True,
            content=ft.Column(
                expand=False,
                controls=[
                    self.version_dropdown,
                    self.install_button
                ]
            ),
            actions=[ft.TextButton("Close", on_click=lambda e: page.close(self.installation_window))]
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


        # ---- View ----


        self.view = ft.View(
            "/",
            [ft.Text(name.upper(), size=30, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE)],
            padding=10,
            spacing=20,
            vertical_alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
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

        self.refresh()

    
    def refresh(self):
        versions = get_versions()
        last_played = app_settings.get_setting(AppData.LAST_PLAYED)
        self.installed_options = [ft.DropdownOption(v) for v in versions["installed"]]
        self.releases_options = [ft.DropdownOption(v) for v in versions["releases"]]
        if not self.releases_options:
            self.releases_options.append(ft.DropdownOption("1.21.5"))
        try:
            self.installed_dropdown.options = self.installed_options
            self.installed_dropdown.options.insert(0, ft.DropdownOption("Lastest release"))
            if last_played != "" and last_played in versions["installed"]:
                self.installed_dropdown.value = last_played
            else:
                self.installed_dropdown.value = "Lastest release"
                if last_played != "":
                    app_settings.save_settings(AppData.LAST_PLAYED, "")
            self.version_dropdown.options = self.releases_options
            self.version_dropdown.value = self.releases_options[0].key
        except Exception as e:
            print(f"Error: {e}")
        self.play_button.text = "PLAY" if mll.utils.is_minecraft_installed(app_settings.return_mc_directory()) else "INSTALL"
        self.username_input.value = app_settings.get_setting(AppData.USERNAME)
        self.username_text.value = app_settings.get_setting(AppData.USERNAME)
        self.info_minecraft_dir.value = f"Minecraft directory: {app_settings.return_mc_directory()}"
        self.maximum_ram_slider.value = int(re.search(r"\d+", app_settings.get_setting(AppData.JVM_ARGUMENTS)[0]).group())
        self.page.update()
        print("Refresh!")


    def set_username(self, e):
        username: str = self.username_input.value
        if len(username) >= 3 and len(username) <= 16 and " " not in username:
            app_settings.save_settings(AppData.USERNAME, username)
            self.username_input.error_text = None
            self.page.close(self.username_window)
            self.refresh()
        else:
            self.username_input.error_text = "Enter a valid username"
            self.page.update()


    def set_settings(self, e):
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
            self.refresh()
        

    
    def ui_launch_game(self, e):
        selected_version = self.installed_dropdown.value

        if not selected_version:
            self.status_text.value = "Please select a version."
            return
        
        if selected_version == "Lastest release":
            selected_version = mll.utils.get_latest_version()["release"]
            if selected_version not in get_versions()["installed"]:
                self.ui_install_game(None, selected_version)
                return
            app_settings.save_settings(AppData.LAST_PLAYED, "")
        else:
            # Save the last played version
            app_settings.save_settings(AppData.LAST_PLAYED, selected_version)
        
        # Run in a thread to avoid blocking the Flet UI
        buttons_to_disable = [self.play_button, self.install_button, self.version_dropdown, self.installed_dropdown, self.username_input]
        thread = threading.Thread(target=launch_game, args=(self.page, selected_version, self.status_text, buttons_to_disable, self.play_button, self.refresh))
        thread.daemon = True
        thread.start()

    
    def ui_install_game(self, e, version: str = None):
        if not version:
            selected_version = self.version_dropdown.value
        else:
            selected_version = version

        if not selected_version:
            self.status_text.value = "Please select a version."
            return
        
        try:
            self.page.close(self.installation_window)
        except:
            pass
        self.page.open(self.progress_window)
        buttons_to_disable = [self.play_button, self.install_button, self.version_dropdown, self.installed_dropdown, self.username_input]
        thread = threading.Thread(target=install_version, args=(self.page, selected_version, buttons_to_disable, self.progress_window, self.progress_bar, self.status_text, self.refresh))
        thread.daemon = True
        thread.start()
# This file is part of PYZ-LAUNCHER-FOR-MINECRAFT (https://github.com/ZadkielAvendano/PyZ-Launcher-for-Minecraft)
# Copyright (c) 2025 Zadkiel Avendano and collaborators
# License-Identifier: MIT License

import flet as ft
from modules.app_config import *
from modules.launcher import *
from widgets.ui import *
from widgets.app import WindowTittleBar
import minecraft_launcher_lib as mll
import json
import os
import re


## ----- FLET UI -----


class LauncherProfilesView():
    def __init__(self, page: ft.Page):
        self.page = page

        self.versions_options: list[ft.DropdownOption] = []

        self.profile_name_input = ft.TextField(
            label="Launcher profile name",
            width=300,
            border_color=ft.Colors.WHITE24,
            color=ft.Colors.WHITE,
            focused_bgcolor="#4A4A4A",
            focused_border_color=ft.Colors.PRIMARY
        )

        self.version_type_dropdown = ft.Dropdown(
            value="release",
            label="Version type",
            hint_text="Select a version type",
            options=[
                ft.DropdownOption("vanilla", "Vanilla"),
                ft.DropdownOption("custom", "Custom"),
                # Preparing to add support for Forge and Fabric
                #ft.DropdownOption("fabric", "Fabric"),
                #ft.DropdownOption("forge", "Forge")
                ],
            width=300,
            bgcolor="#3C3C3C",
            border_color=ft.Colors.WHITE24,
            color=ft.Colors.WHITE,
            #on_change=self.refresh_versions
        )

        self.version_category_dropdown = ft.Dropdown(
            value="release",
            label="Version category",
            hint_text="Select a version category",
            options=[
                ft.DropdownOption("release", "Release"),
                ft.DropdownOption("snapshot", "Snapshot"),
                ft.DropdownOption("old_beta", "Beta"),
                ft.DropdownOption("old_alpha", "Alpha")
                ],
            width=300,
            bgcolor="#3C3C3C",
            border_color=ft.Colors.WHITE24,
            color=ft.Colors.WHITE,
            on_change=self.refresh_versions
        )

        self.version_dropdown = ft.Dropdown(
            label="Game version",
            hint_text="Select a version",
            options=self.versions_options,
            width=300,
            bgcolor="#3C3C3C",
            border_color=ft.Colors.WHITE24,
            color=ft.Colors.WHITE
        )

        self.confirm_button = ft.FilledButton(
            text="Apply",
            on_click=lambda e: self.set_launcher_profile(),
            width=300,
            height=50,
            style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=5)),
            tooltip="Apply launcher profile"
        )

        self.new_launcher_profile_button = ft.FilledButton(
            text="New launcher profile",
            on_click=self.edit_launcher_profile,
            width=300,
            height=50,
            style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=5)),
            tooltip="Apply"
        )

        self.launcher_profiles_window = ft.AlertDialog(
            modal=True,
            title="Minecraft Launcher Profile",
            bgcolor="#3C3C3C",
            scrollable=True,
            content=ft.Column(
                expand=False,
                controls=[
                    self.profile_name_input,
                    self.version_type_dropdown,
                    self.version_category_dropdown,
                    self.version_dropdown,
                    self.confirm_button
                ]
            ),
            actions=[ft.TextButton("Close", on_click=lambda e: page.close(self.launcher_profiles_window))]
        )

        
        # ---- View ----


        self.view = ft.View(
            "/launcher-profiles",
            [],
            padding=ft.padding.only(left=50, right=50, top=20, bottom=20),
            spacing=20,
            vertical_alignment=ft.MainAxisAlignment.START,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            appbar=WindowTittleBar(
                    self.page,
                    title_text=ft.Text("Launcher Profiles", size=25, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                    custom_actions=[
                        ft.IconButton(
                            icon=ft.Icons.ADD_CIRCLE,
                            tooltip="New launcher profile",
                            on_click=self.edit_launcher_profile
                        )
                    ]
                ),
            bgcolor=ft.Colors.TRANSPARENT,
            decoration=ft.BoxDecoration(
                image=ft.DecorationImage(
                    src="/background_2.png",
                    fit=ft.ImageFit.COVER,
                    color_filter=ft.ColorFilter(color=ft.Colors.with_opacity(0.9, "#3C3C3C"), blend_mode=ft.BlendMode.MULTIPLY)
                )
            ),
            scroll=True
        )



    def refresh_versions(self, e: ft.Control = None):
        """
        Refreshes the available versions in the dropdown based on the selected category.
        """
        versions = get_versions()

        # Retrieve available versions
        self.versions_options = [ft.DropdownOption(v) for v in versions[self.version_category_dropdown.value]]

        try:
            # Configure available versions dropdown
            self.version_dropdown.options = self.versions_options
            self.version_dropdown.value = self.versions_options[0].key

        except Exception as e:
            print(f"Error: {e}")

        finally:
            self.page.update()



    def edit_launcher_profile(self, e: ft.Control = None, edit_profile: mll.types.VanillaLauncherProfile = None):
        """
        Updates UI controls based on the given launcher profile.

        If editing a profile, it loads existing settings; otherwise, it prepares controls for creating a new profile.
        """
        if edit_profile:
            # Editing an existing profile
            version_type = edit_profile["versionType"]
            
            if version_type in {"latest-release", "latest-snapshot"}:
                # Settings for 'latest-release' or 'latest-snapshot' versions
                self.profile_name_input.value = version_type.replace("-", " ").capitalize()
                self.version_type_dropdown.value = "vanilla"
                # Determine the category: 'release' if latest-release, else 'snapshot'
                category = "release" if version_type == "latest-release" else "snapshot"
                self.version_category_dropdown.value = category

                # Retrieve the latest version based on the category
                latest_versions = mll.utils.get_latest_version()
                latest_version = latest_versions.get(category)
                self.version_dropdown.options = [ft.DropdownOption(latest_version)]
                self.version_dropdown.value = latest_version
                self.version_category_dropdown.visible = True

            else:
                # Settings for profiles that do not use the "latest" versions
                # Use the provided "name" if available, otherwise fallback to "version"
                self.profile_name_input.value = edit_profile["name"] if edit_profile["name"] != "" else edit_profile["version"]
                self.version_dropdown.options = [ft.DropdownOption(edit_profile["version"])]
                self.version_dropdown.value = edit_profile["version"]

                if mll.utils.is_vanilla_version(edit_profile["version"]):
                    self.version_type_dropdown.value = "vanilla"
                    # Iterate through the versions dictionary to identify the version category
                    for category, version_list in get_versions().items():
                        if self.version_dropdown.value in version_list:
                            self.version_category_dropdown.value = category
                            print(f"Category: {category}, version: {self.version_dropdown.value}")
                            break
                    self.version_category_dropdown.visible = True
                else:
                    self.version_type_dropdown.value = "custom"
                    self.version_category_dropdown.visible = False

            # Disable UI controls to prevent further editing
            self.profile_name_input.disabled = True
            self.version_category_dropdown.disabled = True
            self.version_type_dropdown.disabled = True
            self.version_dropdown.disabled = True
            self.confirm_button.visible = False

        else:
            # Settings for creating a new profile
            self.profile_name_input.value = ""
            self.version_category_dropdown.value = "release"
            self.version_type_dropdown.value = "vanilla"

            # Enable necessary UI controls for a new profile
            self.version_category_dropdown.visible = True
            self.profile_name_input.disabled = False
            self.version_category_dropdown.disabled = False
            self.version_type_dropdown.disabled = True  # Assuming the type is fixed as "vanilla" by default
            self.version_dropdown.disabled = False
            self.confirm_button.visible = True

            # Refresh the available versions in the dropdown
            self.refresh_versions()

        # Open the launcher profiles window and update the UI page
        self.page.open(self.launcher_profiles_window)
        self.page.update()



    def set_launcher_profile(self, edit_profile: mll.types.VanillaLauncherProfile = None):
        """
        Sets or updates a Minecraft launcher profile.
        
        If an existing profile is provided, it searches for its key. If not, it creates a new custom profile.
        """
        if edit_profile:
            #with open(os.path.join(app_settings.return_mc_directory(), "launcher_profiles.json"), "r", encoding="utf-8") as f:
            #        data = json.load(f)
            pass
        else:
            profile: mll.types.VanillaLauncherProfile = {
                "name": self.profile_name_input.value if self.profile_name_input.value else self.version_dropdown.value,
                "version": self.version_dropdown.value,
                "versionType": "custom"
            }
            mll.vanilla_launcher.add_vanilla_launcher_profile(app_settings.return_mc_directory(), profile)
            print(f"The player profile was established: {profile['name']}")
            app_settings.save_settings(AppData.LAST_PLAYED, profile["version"])
            self.page.close(self.launcher_profiles_window)
            refresh()

    

    def remove_launcher_profile(self, edit_profile: mll.types.VanillaLauncherProfile, launcher_option: LauncherProfileOption):
        # Working on the next update
        pass



    def refresh_ui(self, e=None):
        """
        Refreshes the UI by loading Vanilla Launcher profiles.
        
        If none exist, it creates default profiles and ensures the launcher_profiles.json file is present.
        """
        # Vanilla Launcher Profiles
        if mll.vanilla_launcher.do_vanilla_launcher_profiles_exists(app_settings.return_mc_directory()):
            self.view.controls = []
            for profile in mll.vanilla_launcher.load_vanilla_launcher_profiles(app_settings.return_mc_directory()):
                self.view.controls.append(LauncherProfileOption(launcher_profile=profile, on_edit=lambda p: self.edit_launcher_profile(edit_profile=p),
                                                                on_remove=lambda p, o: self.remove_launcher_profile(edit_profile=p, launcher_option=o)))
            self.view.controls.append(self.new_launcher_profile_button)
        else:
            # Add the default profiles ["latest-release", "latest-snapshot"]
            default_profiles: list[mll.types.VanillaLauncherProfile] = [
                {"name": "", "versionType": "latest-release"},
                {"name": "", "versionType": "latest-snapshot"}
            ]
            # Create launcher_profiles.json file if it doesn't exist
            with open(os.path.join(app_settings.return_mc_directory(), "launcher_profiles.json"), "w", encoding="utf-8") as f:
                json.dump({"profiles": {}}, f, ensure_ascii=False, indent=4)

            # Add default profiles
            for profile in default_profiles:
                mll.vanilla_launcher.add_vanilla_launcher_profile(app_settings.return_mc_directory(), profile)
            refresh()

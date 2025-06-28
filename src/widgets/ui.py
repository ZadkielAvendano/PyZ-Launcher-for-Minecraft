# This file is part of PYZ-LAUNCHER-FOR-MINECRAFT (https://github.com/ZadkielAvendano/PyZ-Launcher-for-Minecraft)
# Copyright (c) 2025 Zadkiel Avendano and collaborators
# License-Identifier: MIT License

import flet as ft
import minecraft_launcher_lib as mll


class LauncherProfileOption(ft.ListTile):
    def __init__(self, launcher_profile: mll.types.VanillaLauncherProfile, on_edit=None, on_remove=None):
        super().__init__()
        self.launcher_profile = launcher_profile
        self.title=ft.Text(
            launcher_profile.get("name")
            if launcher_profile.get("versionType") == "custom"
            else launcher_profile.get("versionType", "").replace("-", " ").capitalize(),
            size=20,
            weight=ft.FontWeight.BOLD
        )
        self.subtitle=ft.Text(launcher_profile.get("version", ""))
        self.bgcolor=ft.Colors.with_opacity(0.9, "#3C3C3C")
        self.toggle_inputs=True
        self.height=75
        self.width=1000
        self.shape=ft.RoundedRectangleBorder(10)
        self.leading=ft.Icon(ft.Icons.LAUNCH)
        self.trailing=ft.PopupMenuButton(
            icon=ft.Icons.MORE_VERT,
            bgcolor=ft.Colors.GREY_800,
            items=[
                ft.PopupMenuItem(text="View", on_click=lambda e: on_edit(self.launcher_profile)), # Edit profile feature is planned for the next version.
                #ft.PopupMenuItem(text="Remove", on_click=lambda e: on_remove(self.launcher_profile, self)), # Working on the next update
            ],
        )
        self.on_click=lambda e: on_edit(self.launcher_profile)

        if self.launcher_profile.get("versionType") != "custom":
            if len(self.trailing.items) > 1:
                self.trailing.items.pop()

        # menu = ft.Row(alignment=ft.MainAxisAlignment.END, vertical_alignment=ft.CrossAxisAlignment.CENTER, width=100, controls=[ft.IconButton(icon=ft.Icons.DELETE, icon_color=ft.Colors.ERROR), ft.IconButton(icon=ft.Icons.EDIT)])

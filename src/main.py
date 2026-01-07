# This file is part of PYZ-LAUNCHER-FOR-MINECRAFT (https://github.com/ZadkielAvendano/PyZ-Launcher-for-Minecraft)
# Copyright (c) 2025 Zadkiel Avendano and collaborators
# License-Identifier: MIT License

import flet as ft
from modules.app_config import *
from modules.refresh_handler import *
from widgets.app import WindowTittleBar

fonts = {
    "Poppins-Light": "/fonts/Poppins-Light.ttf",
    "Poppins-Medium": "/fonts/Poppins-Medium.ttf",
    "Poppins-Regular": "/fonts/Poppins-Regular.ttf"
}

theme_transition = ft.PageTransitionTheme.ZOOM

theme = ft.Theme(
    color_scheme_seed=ft.Colors.GREEN,
    font_family="Poppins-Regular",
    page_transitions=ft.PageTransitionsTheme(
        windows=theme_transition,
        macos=theme_transition,
        linux=theme_transition
    ),
    icon_button_theme=ft.IconButtonTheme(shape=ft.RoundedRectangleBorder(radius=20)),
    filled_button_theme=ft.FilledButtonTheme(
        bgcolor=ft.Colors.GREEN_ACCENT_700,
        foreground_color=ft.Colors.WHITE,
        disabled_bgcolor=ft.Colors.GREY_700,
        ),
    appbar_theme=ft.AppBarTheme(surface_tint_color=ft.Colors.SURFACE)
)


style=ft.ButtonStyle(
                bgcolor={
                    ft.ControlState.DEFAULT: ft.Colors.GREEN_ACCENT_700,
                    ft.ControlState.DISABLED: ft.Colors.GREY_700
                    },
                shape=ft.RoundedRectangleBorder(radius=5),
                padding=15,
            )

def main(page: ft.Page):
    page.title = f"{app_name} - {app_version}"
    page.window.width = 1000
    page.window.height = 700
    page.window.min_height = 500
    page.window.min_width = 600
    page.window.title_bar_hidden = True
    page.window.title_bar_buttons_hidden = True
    page.window.center()
    page.theme = theme
    page.fonts = fonts
    page.theme_mode = ft.ThemeMode.DARK
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.bgcolor = ft.Colors.TRANSPARENT
    page.decoration = ft.BoxDecoration(
        image=ft.DecorationImage(
            src="/background.png",
            fit=ft.ImageFit.COVER,
            opacity=0.25
        )
    )

    # LOADING...
    page.appbar = WindowTittleBar(page)
    page.add(ft.Text(value="Loading...", size=28, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE, text_align=ft.TextAlign.CENTER))
    page.add(ft.ProgressRing(color=ft.Colors.ON_SURFACE))
    page.update()

    # Load settings
    init_settings(page)

    # Import views
    from views.home_view import HomeView
    from views.launcher_profiles_view import LauncherProfilesView

    # Load views
    launcher_profiles_view = LauncherProfilesView(page)
    home_view = HomeView(page, launcher_profiles_view)

    # Configure refresh states
    refresh_list.append(home_view.refresh_ui)
    refresh_list.append(launcher_profiles_view.refresh_ui)

    # Store views in app settings
    app_settings.views["home_view"] = home_view
    app_settings.views["launcher_profiles_view"] = launcher_profiles_view

    def route_change(e):
        page.views.clear()
        page.views.append(home_view.view)
        if page.route == "/launcher-profiles":
            page.views.append(launcher_profiles_view.view)
            page.title = f"{app_name} - Launcher Profiles - {app_version}"
        else:
            page.title = f"{app_name} - {app_version}"
        page.update()

    def view_pop(e):
        page.go("/")
        if page.views:
            if page.route == "/launcher-profiles":
                page.go("/")
            else:
                page.go("/")
        else:
            page.go("/")

    page.on_route_change = route_change
    page.on_view_pop = view_pop
    page.go(page.route)
    page.clean()
    refresh()

if __name__ == "__main__":
    ft.app(target=main, assets_dir="assets")
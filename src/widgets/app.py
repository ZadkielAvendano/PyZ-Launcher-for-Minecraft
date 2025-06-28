import flet as ft

class WindowTittleBar(ft.AppBar):
    def __init__(self, page:ft.Page, leading = None, title_text = None, custom_actions = None, bgcolor = None):
        super().__init__(leading=leading)
        self.bgcolor = "#3C3C3C" if not bgcolor else bgcolor
        self.force_material_transparency = True
        if not title_text:
            title_text = ft.Text(page.title)
        self.title = ft.WindowDragArea(content=ft.Row(expand=True, controls=[title_text]))
        self.actions = [
            ft.IconButton(ft.Icons.MINIMIZE, tooltip="Minimize window", on_click=lambda _: self.minimize_window()),
            ft.IconButton(ft.Icons.RECTANGLE_OUTLINED, tooltip="Maximize window", on_click=lambda _: self.maximize_window()),
            ft.IconButton(ft.Icons.CLOSE, tooltip="Close launcher", on_click=lambda _: page.window.close())
        ]
        if custom_actions:
            self.actions.insert(0, ft.Container(width=10))
            for custom_action in custom_actions:
                self.actions.insert(0, custom_action)

    def maximize_window(self):
        self.page.window.maximized = False if self.page.window.maximized else True
        self.page.update()

    def minimize_window(self):
        self.page.window.minimized = False if self.page.window.minimized else True
        self.page.update()
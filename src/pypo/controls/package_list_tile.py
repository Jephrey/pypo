import flet as ft


class PackageListTile(ft.ListTile):
    def __init__(self, name: str, subtitle: str, latest_version: str, listview: ft.ListView, **kwargs):
        super().__init__()

        self.leading = None
        self.title = ft.Text(name, width=200)
        self.subtitle = ft.Text(subtitle)
        self.data = {
            "name": name,
            "latest_version": latest_version,
            "listview": listview,
        }
        # self.on_click=on_tile_clicked
        self.dense = True
        self.is_three_line = True
        # self.url=f"https://pypi.org/project/{name}/"

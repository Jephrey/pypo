import os
from enum import IntEnum

import flet as ft
from flet_core import margin

from package_list_tile import PackageListTile
from util import app_state
from util.packages import run_pip


def on_tile_clicked(e: ft.ControlEvent):
    print(e.control.data)


def on_hover(e: ft.ControlEvent):
    """
    When mouse hovers over a container which contains a list tile.

    :param e:
    :return:
    """
    tile: ft.ListTile = e.control.content
    lv: ft.ListView = tile.data.get("listview")

    # Remove all trailing widgets from all list tiles.
    # An on_blur event on each container or list tile is not (yet) available.
    container: ft.Container
    for container in lv.controls:
        lv_tile = container.content
        lv_tile.trailing = None

    # Set the widgets for the tile being hovered over.
    width = 40
    name = tile.data.get("name")
    floating_buttons = [
        ft.IconButton(
            icon=ft.icons.OPEN_IN_BROWSER_OUTLINED,
            tooltip="Go to webpage",
            url=f"https://pypi.org/project/{name}/"
        )
    ]

    # Insert an icon button to update to the latest version if available.
    latest_version = tile.data.get("latest_version")
    if latest_version:
        width += 40
        floating_buttons.insert(0, ft.IconButton(
            icon=ft.icons.UPDATE_OUTLINED,
            tooltip=f"Update to version {latest_version}",
        ))

    tile.trailing = ft.Row(
        width=width,
        controls=floating_buttons)

    lv.update()


class SelectedPackages(IntEnum):
    PACKAGES_ALL = 1
    PACKAGES_UPTODATE = 2
    PACKAGES_OUTDATED = 3


class PackagesListView(ft.ListView):
    def __init__(self, venv: str = None, **kwargs):
        """

        :param venv: Path to virtual environment.
        :param kwargs:
        """
        super().__init__()
        self.venv = venv
        self.selected: int = SelectedPackages.PACKAGES_ALL
        self.all: list = []
        self.uptodate: list = []
        self.outdated: list = []
        self.filtered: list = []

        self.expand = 1
        self.spacing = 10
        self.padding = 20
        self.auto_scroll = False
        self.divider_thickness = 2

    def get_packages(self) -> str:
        if self.venv is None:
            return "No virtual environment provided."

        pip = f"{self.venv}/bin/pip"
        if not os.path.exists(pip):
            return f"pip command not found: '{pip}'."

        # Run the pip command in the virtual environment.
        # Once for up-to-date packages and once for outdated packages.
        self.uptodate = run_pip(pip)
        self.outdated = run_pip(pip, outdated=True)
        self.all = self.uptodate + self.outdated
        self.selected = SelectedPackages.PACKAGES_ALL
        self.uptodate.sort(key=lambda pkg: pkg[0].lower())
        self.outdated.sort(key=lambda pkg: pkg[0].lower())
        self.all.sort(key=lambda pkg: pkg[0].lower())

        return ""

    def fill(self) -> None:
        # If the filtered list is empty then use one of the others.
        if not self.filtered:
            if self.selected == SelectedPackages.PACKAGES_ALL:
                self.filtered = self.all
            elif self.selected == SelectedPackages.PACKAGES_UPTODATE:
                self.filtered = self.uptodate
            elif self.selected == SelectedPackages.PACKAGES_OUTDATED:
                self.filtered = self.outdated

        # If there is a search value, apply that to the filtered packages.
        if app_state.search:
            self.filtered = filter(lambda p: app_state.search in p[0], self.filtered)
        self.controls.clear()
        for package in self.filtered:
            name = package[0]
            version = package[1]
            latest_version = package[2]
            if latest_version == "":
                subtitle = version
                icon = ft.icons.RECTANGLE_OUTLINED
            else:
                subtitle = f"{version} -> {latest_version}\nUpdate available"
                icon = ft.icons.UPDATE_ROUNDED

            tile = PackageListTile(
                leading=None,
                title=ft.Text(name, width=200),
                subtitle=subtitle,
                name=name,
                latest_version=latest_version,
                # on_click=on_tile_clicked,
                dense=True,
                is_three_line=True,
                listview=self
                # url=f"https://pypi.org/project/{name}/"
            )

            lv_item = ft.Container(
                margin=margin.only(right=10),
                content=tile,
                on_hover=on_hover,
            )
            self.controls.append(lv_item)

    def show(self) -> None:
        """
        Show the packages in the List View.

        :return: None.
        """
        self.fill()
        self.update()

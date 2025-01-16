from contextlib import contextmanager

from nicegui import ui
from nicegui.page_layout import LeftDrawer, RightDrawer

from bewegungskalender.frontend.layout.menu import main_menu, secondary_menu
from bewegungskalender.frontend.navigation.router import Router, ROUTER


@contextmanager
def header(ld:LeftDrawer, rd:RightDrawer=None):
    with ui.header().classes('fixed h-50px flex-nowrap bg-accent m-0 px-3 py-2 items-center max-sm:hidden'):
        with ui.button_group().props('flat'):
            main_menu(ld)
        ui.space().classes('max-sm:hidden')
        with ui.row().classes('max-lg:hidden m-0 p-0'):
            with ui.button_group().props('flat'):
                secondary_menu(ld)
        ui.space().classes('max-sm:hidden lg:hidden')

        ui.button("Filter", icon='filter_alt', on_click=lambda: rd.toggle()).props(
            "flat color=white").classes('max-sm:hidden lg:hidden').bind_visibility_from(ROUTER, "current_page", backward=lambda e: e is not None and (e.path == "/" or e.path == "/karte"))

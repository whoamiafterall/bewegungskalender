from contextlib import contextmanager

from nicegui import ui
from nicegui.page_layout import LeftDrawer, RightDrawer

from bewegungskalender.frontend.main.menu import main_menu, secondary_menu

@contextmanager
def header(ld:LeftDrawer, rd:RightDrawer):
    with ui.header(elevated=True).classes('fixed h-50px flex-nowrap m-0 px-3 py-2 items-center max-[430px]:hidden'):
        with ui.button_group().props('flat'):
            main_menu(ld)
        ui.space().classes('max-sm:hidden')
        with ui.row().classes('max-lg:hidden m-0 p-0'):
            with ui.button_group().props('outline rounded'):
                secondary_menu(ld)
        ui.space().classes('max-sm:hidden')
        ui.button("Filter", icon='filter_alt', on_click=lambda: rd.toggle()).props(
            'flat color=white').classes('max-sm:hidden')

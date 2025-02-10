from contextlib import contextmanager

from nicegui import ui
from nicegui.page_layout import LeftDrawer, RightDrawer

from bewegungskalender.frontend.filter.filters.time_filter import month_filter_ui
from bewegungskalender.frontend.helpers.functions import filter_visibility
from bewegungskalender.frontend.layout.menu import main_menu, secondary_menu
from bewegungskalender.frontend.navigation.router import ROUTER


@contextmanager
def header(ld: LeftDrawer, rd: RightDrawer):
	with ui.header().classes('fixed h-50px max-sm:hidden flex-nowrap bg-accent m-0 px-3 py-2 items-center'):
		with ui.button_group().props('flat dense'):
			main_menu(ld, rd, props='flat')
		ui.space().classes()
		with filter_visibility(paths='/'):
			month_filter_ui()
		ui.space().classes('max-lg:hidden')
		with ui.row().classes('max-lg:hidden'):
			with ui.button_group().props('flat'):
				secondary_menu(ld)
from nicegui import ui
from nicegui.page_layout import RightDrawer, LeftDrawer

from bewegungskalender.frontend.filter.filters.category_filter import categories_filters_ui
from bewegungskalender.frontend.filter.filters.duration_filter import duration_filter_ui
from bewegungskalender.frontend.filter.filters.location_proximity_filter import location_proximity_filter_ui
from bewegungskalender.frontend.layout.menu import secondary_menu


def left_drawer() -> LeftDrawer:
	with ui.left_drawer(value=False, fixed=True).classes('py-3 items-stretch lg:hidden bg-primary') as ld:
			ui.space().classes('sm:hidden')
			secondary_menu(ld, 'bg-accent w-5/6 mx-auto p-2 text-sm font-normal normal-case', 'color=contrast')
			ui.button(icon='close', on_click=lambda: ld.hide()).props('flat color=contrast align=center').classes(
				'h-24px')
	return ld

async def right_drawer() -> RightDrawer:
	with ui.right_drawer(value=False, fixed=True).classes('p-3 gap-1 text-sm px-3 items-stretch w-full bg-primary lg:hidden m-0').props(
				'width=auto') as rd:
			ui.space().classes('sm:hidden')
			duration_filter_ui()
			location_proximity_filter_ui()
			await categories_filters_ui()
			ui.button(icon='close', on_click=lambda: rd.hide()).props('flat color=contrast align=center').classes(
				'h-24px')
	return rd
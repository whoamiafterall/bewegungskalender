from nicegui import ui
from nicegui.page_layout import RightDrawer, LeftDrawer

from bewegungskalender.frontend.filter.ui.category_filter import category_filters
from bewegungskalender.frontend.filter.ui.location_filter import location_filter
from bewegungskalender.frontend.filter.ui.time_filter import duration_filter
from bewegungskalender.frontend.main.menu import secondary_menu


def left_drawer() -> LeftDrawer:
	with ui.left_drawer(value=False, fixed=True, elevated=True, top_corner=True).classes('p-0 m-0 lg:hidden bg-primary').props(
			'width=auto') as ld:
		with ui.column(wrap=False, align_items='stretch').classes('w-full p-5'):
			secondary_menu(ld, 'bg-accent text-sm font-normal normal-case')
			ui.button(icon='close', on_click=lambda: ld.hide()).props('flat color=white align=center').classes(
				'h-24px')
	return ld

async def right_drawer() -> RightDrawer:
	with ui.right_drawer(value=False, fixed=True, elevated=True, top_corner=False).classes('p-0 m-0').props(
			'width=auto') as rd:
		with ui.column(wrap=False, align_items='start').classes('m-0 gap-1 max-w-1/4 pt-5 px-3 shrink text-sm lg:hidden'):
			duration_filter()
			location_filter()
			await category_filters()
	return rd
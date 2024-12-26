from nicegui import ui
from nicegui.page_layout import RightDrawer, LeftDrawer

from bewegungskalender.backend.calendar.location import EventLocationType
from bewegungskalender.frontend.filter.filters.category_filter import categories_filters_ui
from bewegungskalender.frontend.filter.filters.location_proximitry_filter import location_proximity_filter_ui
from bewegungskalender.frontend.filter.filters.location_type_filter import location_type_filter_ui, LOCATION_TYPE_FILTER
from bewegungskalender.frontend.filter.filters.duration_filter import duration_filter_ui
from bewegungskalender.frontend.main.menu import secondary_menu
from bewegungskalender.frontend.navigation.router import ROUTER


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

			duration_filter_ui()
			location_type_filter_ui().bind_visibility_from(ROUTER,"current_page",lambda e: e is not None and (e.path == "/"))

			# temporary workaround due to nice gui not having the option to bind visibility from multiple attributes
			with ui.list().classes("w-full").bind_visibility_from(ROUTER, 'current_page',lambda e: e is not None and (e.path == "/karte")):
				location_proximity_filter_ui()
			with ui.list().classes("w-full").bind_visibility_from(ROUTER, 'current_page',lambda e: e is not None and (e.path == "/")):
				location_proximity_filter_ui().bind_visibility_from(LOCATION_TYPE_FILTER.state, target_name="value", backward=lambda v: (EventLocationType.offline in v))

			await categories_filters_ui()
	return rd
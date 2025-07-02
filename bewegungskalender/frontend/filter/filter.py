from more_itertools.more import distinct_permutations
from nicegui import ui
from nicegui.page_layout import RightDrawer
from sqlmodel import select
from sqlalchemy import create_engine, func

from bewegungskalender.backend.calendar.category import Category
from bewegungskalender.backend.calendar.event import Event
from bewegungskalender.backend.calendar.event_instance import EventInstance
from bewegungskalender.backend.calendar.location import Location
from bewegungskalender.backend.io.db import DB
from bewegungskalender.frontend.navigation.router import ROUTER


def call_refresh_filter_event():
	ui.run_javascript("emitEvent('refresh_filter');")


def events_using_filters(filters: [],distinct: bool) -> list[EventInstance]:
	# init select
	statement = select(EventInstance, Event, Location, Category)
	
	# Add where clauses from filters
	for single_filter in filters:
		statement = single_filter.apply_filter_to_statement(statement)

	statement = statement.join(EventInstance).join(Location).join(Category).order_by(EventInstance.start).order_by(Event.summary)
	if distinct:
		statement = statement.group_by(Event.id)

	database = DB()

	# run statement
	result = database.exe(statement).all()

	for result1 in [n.EventInstance for n in result]:
		print(result1)

	# return as array of Events
	return [n.EventInstance for n in result]


def filter_sticky(right_drawer: RightDrawer):
	with ui.page_sticky(x_offset=18, y_offset=18).style("z-index: 1000;").bind_visibility_from(ROUTER, "show_filter"):
		ui.button(icon="filter_alt", on_click=lambda: right_drawer.toggle()).props('fab color=accent').classes(
			'max-sm:hidden md:hidden')

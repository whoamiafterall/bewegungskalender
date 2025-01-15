from nicegui import ui
from sqlmodel import select

from bewegungskalender.backend.calendar.category import Category
from bewegungskalender.backend.calendar.event import Event
from bewegungskalender.backend.calendar.location import Location
from bewegungskalender.backend.io import db
from bewegungskalender.frontend.functions import loading


def call_refresh_filter_event():
	ui.run_javascript("emitEvent('refresh_filter');")

def events_using_filters(filters: []) -> list[Event]:
	loading('Filter...', 0.1)
	# init select
	statement = select(Event,Location,Category)

	for single_filter in filters:
		statement = single_filter.apply_filter_to_statement(statement)

	# run statement
	statement = statement.join(Location).join(Category).order_by(Event.start).order_by(Event.summary)
	result = db.exe(statement).all()

	# return as array of Events
	return [n.Event for n in result]


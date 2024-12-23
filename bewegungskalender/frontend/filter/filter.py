import math
from datetime import timedelta

from nicegui import ui
from slugify import slugify
from sqlmodel import select, or_, and_

from bewegungskalender.backend.calendar.category import Category
from bewegungskalender.backend.calendar.event import Event
from bewegungskalender.backend.calendar.location import Location
from bewegungskalender.backend.io import db


def call_refresh_filter_event():
	ui.run_javascript("emitEvent('refresh_filter');")

def events_using_filters(filters: []) -> list[Event]:

	# init select
	statement = select(Event,Location,Category)

	for single_filter in filters:
		statement = single_filter.apply_filter_to_statement(statement)

	# run statement
	statement = statement.join(Location).join(Category).order_by(Event.start).order_by(Event.start).limit(25)
	result = db.exe(statement).all()

	# return as array of Events
	return [n.Event for n in result]


import math
from datetime import timedelta

from nicegui import ui
from slugify import slugify
from sqlmodel import select, or_, and_

from bewegungskalender.backend.calendar.category import Category
from bewegungskalender.backend.calendar.event import Event
from bewegungskalender.backend.calendar.location import Location, EventLocationType
from bewegungskalender.backend.io import db
from bewegungskalender.frontend.filter.controllers.category_filter_controller import CATEGORY_FILTER
from bewegungskalender.frontend.filter.controllers.location_proximity_filter_controller import LOCATION_PROXIMITY_FILTER
from bewegungskalender.frontend.filter.controllers.location_type_filter_controller import LOCATION_TYPE_FILTER
from bewegungskalender.frontend.filter.controllers.time_filter_controller import TIME_FILTER

def call_refresh_filter_event():
	ui.run_javascript("emitEvent('refresh_filter');")

def events_using_filter() -> list[Event]:

	# init select
	statement = select(Event,Location,Category)

	statement = TIME_FILTER.apply_filter_to_statement(statement)
	statement = LOCATION_TYPE_FILTER.apply_filter_to_statement(statement)
	statement = LOCATION_PROXIMITY_FILTER.apply_filter_to_statement(statement)
	statement = CATEGORY_FILTER.apply_filter_to_statement(statement)

	# run statement
	statement = statement.join(Location).join(Category).order_by(Event.start).order_by(Event.start).limit(25)
	result = db.exe(statement).all()

	# return as array of Events
	return [n.Event for n in result]


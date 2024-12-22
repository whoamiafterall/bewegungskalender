import math
import sched
import time
from datetime import timedelta

from nicegui import ui, binding
from slugify import slugify
from sqlmodel import select, or_, and_

from bewegungskalender.backend.calendar.category import Category
from bewegungskalender.backend.calendar.event import Event
from bewegungskalender.backend.calendar.location import Location, EventLocationType
from bewegungskalender.backend.io import db
from bewegungskalender.backend.io.config import CALENDARS
from bewegungskalender.libs.exceptions import NoResultError
from bewegungskalender.libs.nominatim import search_city


class LocationTypeFilter:

	def __init__(self):
		self.state = "Überall"
		self.force_offline = False

	@property
	def usable_state(self):
		return "Offline" if self.force_offline else self.state



def call_refresh_filter_event():
	ui.run_javascript("emitEvent('refresh_filter');")

class LocationFilter:

	def __init__(self):
		self.event = None
		self.search_query = ""
		self.search_result = None
		self.scheduler = sched.scheduler(time.time, time.sleep)

	@property
	def query(self):
		return self.search_query

	@query.setter
	def query(self, new_value):
		self.search_query = new_value
		ui.run_javascript("emitEvent('update_location_search');")

	@property
	def result(self):
		return self.search_result

	# this has to be linked to an event listener in main theme.py!
	def run_search(self):
		try:
			self.search_result = search_city(self.search_query)[0]
		except NoResultError:
			self.search_result = None


class FilterController:

	def __init__(self):
		self.categories = {}


		self.location_type = LocationTypeFilter()

		self.location_specific_location = LocationFilter()
		self.location_specific_distance = binding.BindableProperty()
		self.duration = binding.BindableProperty()


		for calendar in CALENDARS:
			self.categories[f"{slugify(str(calendar['calendar']['internal']))}"] = binding.BindableProperty()



	def events_using_filter(self) -> list[Event]:

		# select all needed
		statement = select(Event,Location,Category)

		# time filtering
		#statement = statement.where(Event.start > today())

		#until = datetime.now().__add__(timedelta(days=100))
		#statement = statement.select(Event.start < until)

		# category filtering

		categories = db.exe(select(Category)).all()
		for category in categories:
			if self.categories[f"{slugify(str(category.internal))}"].value is False:
				statement = statement.where(
					Category.name != category.name
				)

		# duration filtering
		duration_series = self.duration.value
		duration_args = []

		if "Mehrtägig" in duration_series:
			duration_args.append(Event.duration > timedelta(hours=24))
		if "Ganztags" in duration_series:
			duration_args.append(and_(Event.duration > timedelta(hours=6),Event.duration < timedelta(hours=36)))
		if "Kurz" in duration_series:
			duration_args.append(Event.duration <= timedelta(hours=6))

		if len(duration_args) == 1:
			statement = statement.where(duration_args[0])
		elif len(duration_args) > 1:
			statement = statement.where(or_(*duration_args))


		# location filtering
		if self.location_type.usable_state == "Online":
			statement = statement.where(
                Location.type == EventLocationType.online
            )
		else:
			if self.location_specific_location.result is not None:
				distance = self.location_specific_distance.value

				lat = float(self.location_specific_location.result["lat"])
				lon = float(self.location_specific_location.result["lon"])

				max_lat = lat + distance / 110.574
				min_lat = lat - distance / 110.574

				max_lon = lon + distance / 111.320 * math.cos(max_lat * math.pi / 180)
				min_lon = lon - distance / 111.320 * math.cos(min_lat * math.pi / 180)

				operation = and_(
					Location.lat > float(min_lat),
					Location.lat < float(max_lat),
					Location.lon > float(min_lon),
					Location.lon < float(max_lon),
				)
				if self.location_type.usable_state == "Offline":
					statement = statement.where(operation)
				else:
					statement = statement.where(or_(Location.type != EventLocationType.offline, operation))

			elif self.location_type.usable_state == "Offline":
				statement = statement.where(
					Location.type == EventLocationType.offline
				)


		# run statement

		statement = statement.join(Location).join(Category).order_by(Event.start).order_by(Event.start).limit(25)
		result = db.exe(statement).all()
		return [n.Event for n in result]



FILTER = FilterController()
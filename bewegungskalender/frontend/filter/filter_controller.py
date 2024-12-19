import asyncio
import math
import sched
import time
from datetime import timedelta, datetime

from dateutil.utils import today
from nicegui import ui,binding
from sqlmodel import select
from slugify import slugify
from starlette.config import undefined

from bewegungskalender.backend.calendar.category import Category
from bewegungskalender.backend.calendar.event import Event
from bewegungskalender.backend.calendar.location import Location
from bewegungskalender.backend.io import db
from bewegungskalender.libs.nominatim import search_city


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

		# Implemented as suggested here https://github.com/zauberzeug/nicegui/issues/1086 in order to prevent a UI event issue
		# Find event loop
		loop = asyncio.get_event_loop()
		# run in executor
		loop.run_in_executor(None,self.change_executer)

	# cancle old event, enqueue new and run
	def change_executer(self):
		if self.scheduler.queue.__contains__(self.event):
			self.scheduler.cancel(self.event)
			self.event = None
		if self.event is None or len(self.scheduler.queue) == 0:
			self.event = self.scheduler.enter(1, 1, self.search)
		self.scheduler.run()





	@property
	def result(self):
		return self.search_result

	def search(self):
		try:
			self.search_result = search_city(self.search_query)[0]
		except:
			self.search_result = None


class FilterController:

	def __init__(self):
		categories = db.exe(select(Category)).all()
		self.categories = {}
		self.location_type = binding.BindableProperty()
		self.location_specific_location = LocationFilter()

		self.location_specific_location_result = binding.BindableProperty()
		self.location_specific_distance = binding.BindableProperty()
		self.duration = binding.BindableProperty()
		for category in categories:
			self.categories[f"{slugify(str(category.name))}"] = binding.BindableProperty()

	def update_location_specific_location_result(self):
		query = self.location_specific_location_query
		if len(query) <= 1:
			self.location_specific_location_result = None
		else:
			try:
				self.location_specific_location_result = search_city(query)[0]
			except:
				self.location_specific_location_result = None

	#todo: implement other filters
	def events_using_filter(self) -> list[Event]:
		until = datetime.now().__add__(timedelta(days=100))
		if 1 == 2:
			distance = float(round(self.location_distance_slider.value * self.location_distance_slider.value * 10))
			coords = self.location_card_coords
			
			maxlat = coords[0] + distance / 110.574
			minlat = coords[0] - distance / 110.574
			
			maxlon = coords[1] + distance / 111.320*math.cos(maxlat * math.pi / 180)
			minlon = coords[1] - distance / 111.320*math.cos(minlat * math.pi / 180)
			
			
			
			result = db.exe(select(Event,Location).where(
				Event.start > today(),
				Event.start < until,
				Location.lat > float(minlat),
				Location.lat < float(maxlat),
				Location.lon > float(minlon),
				Location.lon < float(maxlon),
				).join(Location).order_by(Event.start)).all()
			
			return [n.Event for n in result]
		else:
			events:list[Event] = db.exe(select(Event).where(Event.start > today(), Event.start < until).order_by(Event.start)).all()
			return events



FILTER = FilterController()
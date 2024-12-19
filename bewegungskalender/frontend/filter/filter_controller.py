import asyncio
import math
import sched
import time
from datetime import timedelta, datetime

from dateutil.utils import today
from docutils.utils.math.tex2mathml_extern import latexml
from nicegui import ui,binding,observables
from sqlmodel import select
from slugify import slugify
from starlette.config import undefined

from bewegungskalender.backend.calendar.category import Category
from bewegungskalender.backend.calendar.event import Event
from bewegungskalender.backend.calendar.location import Location
from bewegungskalender.backend.io import db
from bewegungskalender.libs.nominatim import search_city


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

	##this has to be linked to an event listener in main theme.py!
	def run_search(self):
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

	def events_using_filter(self) -> list[Event]:


		statement = select(Event,Location,Category).where(Event.start > today()) #,Event.start < until

		#until = datetime.now().__add__(timedelta(days=100))
		#statement = statement.select(Event.start < until)

		categories = db.exe(select(Category)).all()
		for category in categories:
			if self.categories[f"{slugify(str(category.name))}"].value is False:
				statement = statement.where(
					Category.name != category.name
				)

		#TODO: Filter Duration

		if self.location_type is "Online":
			statement = statement.where(
				Location.lat == 'None'
			)
		else:
			if self.location_type is "Offline":
				statement = statement.where(
					Location.lat != 'None'
				)
			#TODO: ALLOW online events somehow!
			if self.location_specific_location.result is not None:
				distance = self.location_specific_distance.value

				lat = float(self.location_specific_location.result["lat"])
				lon = float(self.location_specific_location.result["lon"])

				maxlat = lat + distance / 110.574
				minlat = lat - distance / 110.574

				maxlon = lon + distance / 111.320*math.cos(maxlat * math.pi / 180)
				minlon = lon - distance / 111.320*math.cos(minlat * math.pi / 180)

				statement = statement.where(
					Location.lat > float(minlat),
					Location.lat < float(maxlat),
					Location.lon > float(minlon),
					Location.lon < float(maxlon),
					)

			statement = statement.join(Location).join(Category).order_by(Event.start).order_by(Event.start)
			result = db.exe(statement).all()
			return [n.Event for n in result]



FILTER = FilterController()
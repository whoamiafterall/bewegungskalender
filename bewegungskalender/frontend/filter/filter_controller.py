import math
from datetime import timedelta, datetime

from dateutil.utils import today
from nicegui import ui,binding
from sqlmodel import select
from slugify import slugify

from bewegungskalender.backend.calendar.category import Category
from bewegungskalender.backend.calendar.event import Event
from bewegungskalender.backend.calendar.location import Location
from bewegungskalender.backend.io import db
from bewegungskalender.libs.nominatim import search_city



class FilterController:

	def __init__(self):
		categories = db.exe(select(Category)).all()
		self.categories = {}
		self.location_type = binding.BindableProperty()
		self.location_specific = binding.BindableProperty()
		self.location_specific_distance = binding.BindableProperty()
		self.duration = binding.BindableProperty()
		for category in categories:
			self.categories[f"{slugify(str(category.name))}"] = binding.BindableProperty()


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
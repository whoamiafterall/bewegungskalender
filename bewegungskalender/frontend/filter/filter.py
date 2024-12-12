import math
from datetime import timedelta, datetime
from typing import Callable

from dateutil.utils import today
from nicegui import ui
from sqlmodel import select

from bewegungskalender.backend.calendar.event import Event
from bewegungskalender.backend.calendar.location import Location
from bewegungskalender.backend.io import db
from bewegungskalender.libs.nominatim import search_city


# todo manage text via config
class Eventfilter:
	
	def __init__(self,apply_filter: Callable):
		self.timespan_slider = None
		
		with ui.dialog().classes('') as dialog, ui.card():
			
			timespan_slider_label = ui.label("")
			self.timespan_slider = ui.slider(min=10,max=180,step=10,value=30).on('update:model-value', lambda e: update_timespan_slider_label(e.args), throttle=0.1)
			def update_timespan_slider_label(value):
				timespan_slider_label.text = f"Voraussicht: {value} Tage"
			update_timespan_slider_label(self.timespan_slider.value)
			
			
			ui.input(label="Ort",placeholder="Stadt").on('update:model-value',handler= lambda e: update_location_card(e.args), throttle=2.0).props('clearable')
			
			self.location_card = ui.card().classes("w-full m-0 p-4 border no-shadow")
			
			with self.location_card:
				self.location_card_city = ui.label("")
				
				location_distance_slider_label = ui.label("")
				self.location_distance_slider = ui.slider(min=1,max=10,step=0.25,value=1).on('update:model-value', lambda e: update_location_distance_slider_label(e.args), throttle=0.1)
				
				def round_h_h(value):
					return round((value) * 2) / 2
				
				def update_location_distance_slider_label(value):
					dis = round(value * value * 10)
					timemin = (0.5+dis/100)
					timemax = (0.5+dis/55)
					
					if timemax - timemin < 0.5:
						location_distance_slider_label.text = f"Entfernung: {dis}km ({round_h_h(timemax + (timemax - timemin) / 2)}h)"
					else:
						location_distance_slider_label.text = f"Entfernung: {dis}km ({round_h_h(timemin)}-{round_h_h(timemax)}h)"
				
				update_location_distance_slider_label(self.location_distance_slider.value)
				
				#TODO: finisch this up
				ui.checkbox(text="Mehrtägiges auch außerhalb der Entfernung anzeigen",value=True).disable()
			
			
			self.location_card.visible = False
			
			def update_location_card(value):
				if len(value) <= 0:
					self.location_card.visible = False
				else:
					try:
						result = search_city(value)
						self.location_card.visible = True
						print(result[0])
						self.location_card_coords = [float(result[0]["lat"]),float(result[0]["lon"])]
						self.location_card_city.text = result[0]["display_name"]
					
					except:
						self.location_card.visible = False
			
			#TODO: finisch this up
			ui.checkbox(text="Online Events anzeigen?",value=True).disable()
			
			
			ui.button("Anwenden",on_click=lambda: dialog.submit(None))
		
		
		async def show():
			result = await dialog
			apply_filter()
	
	#todo: implement other filters
	def events_using_filter(self) -> list[Event]:
		until = datetime.now().__add__(timedelta(days=self.timespan_slider.value)).strftime('%Y-%m-%d %H:%M:%S')
		if self.location_card.visible:
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


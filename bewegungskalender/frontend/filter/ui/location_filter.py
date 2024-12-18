import math

from nicegui import ui

from bewegungskalender.frontend.filter.filter_controller import FILTER
from bewegungskalender.libs.exceptions import NoResultError
from bewegungskalender.libs.nominatim import search_city


def location_filter():

	(ui.select(["Überall", "Online", "Offline"], label="Ort", value="Überall").bind_value(FILTER.location_type).classes("pl-3 w-full my-1")).props("filled color=secondary")

	ui.input(label="Bestimmter Ort", placeholder="Stadt").bind_value(FILTER.location_specific).props('clearable filled').classes('w-full my-1 pl-3').bind_visibility_from(FILTER.location_type, 'value', lambda v: v != "Offline")
	

	with ui.card().classes("ml-3 gap-0.5 border w-full max-w-[260px] no-shadow").bind_visibility_from(FILTER.location_specific, 'value', lambda v: len(v) > 0):

		ui.label("").bind_text_from(FILTER.location_specific_distance, 'value', backward = lambda a: f"Radius: {a}km")

		ui.slider(min=1, max=10, step=0.25, value=1).bind_value(FILTER.location_specific_distance,backward=lambda i: math.sqrt(i / 10),forward= lambda i: round(i * i * 10)).props('thumb-color=accent selection-color=accent')

		
		def round_h_h(value):
			return round(value * 2) / 2


	
	
	
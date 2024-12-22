import math

from nicegui import ui
from starlette.config import undefined

from bewegungskalender.frontend.filter.controllers.location_filter_controller import LOCATION_FILTER
from bewegungskalender.frontend.filter.filter import call_refresh_filter_event
from bewegungskalender.libs.exceptions import NoResultError
from bewegungskalender.libs.nominatim import search_city


def location_filter():

	(ui.select(["Überall", "Online", "Offline"], label="Ort", value="Überall").on_value_change(call_refresh_filter_event).bind_value(LOCATION_FILTER,"state").classes("pl-3 w-full my-1")).props("filled color=secondary").bind_visibility_from(LOCATION_FILTER,"force_offline",backward=lambda v: v == False)

	with ui.list().classes("w-full").bind_visibility_from(LOCATION_FILTER, 'usable_state', lambda v: v != "Online"):

		ui.input(label="Bestimmter Ort", placeholder="Stadt").bind_value(LOCATION_FILTER.location,"query").props('clearable filled').classes('w-full my-1 pl-3')

		with ui.card().classes("ml-3 gap-0.5 border w-full max-w-[260px] no-shadow").bind_visibility_from(LOCATION_FILTER.location, 'result', lambda v: v is not None):

			ui.label("").bind_text_from(LOCATION_FILTER.location, 'result', backward = lambda a: "" if a is None else a["display_name"])

			ui.input().on_value_change(call_refresh_filter_event).bind_value_from(LOCATION_FILTER.location,"result", backward = lambda a: "" if a is None else a["display_name"]).set_visibility(False)

			ui.label("").bind_text_from(LOCATION_FILTER.distance, 'value', backward = lambda a: f"Radius: {a}km")

			ui.slider(min=1, max=10, step=0.25, value=1).on_value_change(call_refresh_filter_event).bind_value(LOCATION_FILTER.distance,backward=lambda i: math.sqrt(i / 10),forward= lambda i: round(i * i * 10)).props('thumb-color=accent selection-color=accent')



	
	
	
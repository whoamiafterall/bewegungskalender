from nicegui import ui

from bewegungskalender.frontend.filter.controllers.location_filter_controller import LOCATION_FILTER
from bewegungskalender.frontend.filter.filter import call_refresh_filter_event

def online_filter_ui():
	(ui.select(["Überall", "Online", "Offline"], label="Ort", value="Überall")
    .on_value_change(call_refresh_filter_event).bind_value(LOCATION_FILTER, "state")
    .classes("pl-3 w-full my-1")).props("filled color=secondary")
 
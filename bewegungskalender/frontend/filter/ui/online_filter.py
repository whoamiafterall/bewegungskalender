from nicegui import ui

from bewegungskalender.frontend.filter.filter_controller import call_refresh_filter_event, FILTER

def online_filter():
	(ui.select(["Überall", "Online", "Offline"], label="Ort", value="Überall")
    .on_value_change(call_refresh_filter_event).bind_value(FILTER.location_type, "state")
    .classes("pl-3 w-full my-1")).props("filled color=secondary")
 
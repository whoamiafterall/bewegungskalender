from nicegui import ui

from bewegungskalender.frontend.filter.controllers.time_filter_controller import TIME_FILTER
from bewegungskalender.frontend.filter.filter import call_refresh_filter_event

	
def duration_filter_ui():
	(ui.select(["Mehrtägig", "1 Tag", "Stunden"], label="Dauer", value=["Mehrtägig", "1 Tag", "Stunden"],
	           multiple=True, clearable=True).classes("pl-3 w-full my-1")).props("filled color=secondary").on_value_change(call_refresh_filter_event).bind_value(TIME_FILTER.duration)



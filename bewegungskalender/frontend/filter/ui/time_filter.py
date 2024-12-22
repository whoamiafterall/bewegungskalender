from nicegui import ui

from bewegungskalender.frontend.filter.filter_controller import FILTER,call_refresh_filter_event

	
def duration_filter():
	(ui.select(["Mehrtägig", "Ganztags", "Kurz"], label="Dauer", value=["Mehrtägig", "Ganztags", "Kurz"],
	           multiple=True, clearable=True).classes("pl-3 w-full my-1")).props("filled color=secondary").on_value_change(call_refresh_filter_event).bind_value(FILTER.duration)



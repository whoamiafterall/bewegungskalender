from nicegui import ui

from bewegungskalender.frontend.filter.filter_controller import FILTER

	
def duration_filter():
	(ui.select(["Mehrtägig", "1 Tag", "Stunden"], label="Dauer", value=["Mehrtägig", "1 Tag", "Stunden"],
	           multiple=True, clearable=True).classes("pl-3 w-full my-1")).props("filled color=secondary").bind_value(FILTER.duration)
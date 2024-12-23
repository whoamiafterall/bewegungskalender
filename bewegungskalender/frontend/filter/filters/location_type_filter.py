from nicegui import ui
from nicegui.element import Element
from sqlalchemy import Select

from bewegungskalender.backend.calendar.location import Location, EventLocationType
from bewegungskalender.frontend.filter.filter import call_refresh_filter_event

def location_type_filter_ui() -> Element:
	return (ui.select(["Überall", "Online", "Offline"], label="Ort", value="Überall")
    .on_value_change(call_refresh_filter_event).bind_value(LOCATION_TYPE_FILTER, "state")
    .classes("pl-3 w-full my-1")).props("filled color=secondary")


class LocationTypeFilterController:

    def __init__(self):
        self.state = "Überall"

    def apply_filter_to_statement(self,statement: Select):

        if "Online" in self.state:
            return statement.where(Location.type == EventLocationType.online)
        elif "Offline" in self.state:
            return statement.where(Location.type == EventLocationType.offline)
        else:
            return statement


LOCATION_TYPE_FILTER = LocationTypeFilterController()

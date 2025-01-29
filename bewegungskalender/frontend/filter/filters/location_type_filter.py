from nicegui import ui,binding
from nicegui.element import Element
from sqlalchemy import Select

from bewegungskalender.backend.calendar.location import Location, LocationType
from bewegungskalender.frontend.filter.filter import call_refresh_filter_event

def location_type_filter_ui() -> Element:

    return (ui.select(
        {location_type: location_type.keyword for location_type in LocationType}
        , label="Ort", value=[location_type for location_type in LocationType], multiple=True, clearable=True)
    .on_value_change(call_refresh_filter_event).bind_value(LOCATION_TYPE_FILTER.state)
    .classes("pl-3 w-full my-1")).props("outline behavior=menu dense hide-dropdown-icon color=secondary")

class LocationTypeFilterController:

    def __init__(self):
        self.state = binding.BindableProperty()

    def apply_filter_to_statement(self,statement: Select):

        if len(self.state.value) > 0:
            for event_type in LocationType:
                if event_type not in self.state.value:
                    statement = statement.where(Location.type != event_type)

        return statement


LOCATION_TYPE_FILTER = LocationTypeFilterController()


class LocalLocationTypeFilterController:

    def apply_filter_to_statement(self,statement: Select):
        return statement.where(Location.type == LocationType.local)


LOCAL_LOCATION_TYPE_FILTER = LocalLocationTypeFilterController()
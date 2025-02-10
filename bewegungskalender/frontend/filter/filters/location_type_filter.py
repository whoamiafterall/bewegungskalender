from nicegui import ui, binding
from sqlalchemy import Select

from bewegungskalender.backend.calendar.location import Location, LocationType
from bewegungskalender.frontend.filter.filter import call_refresh_filter_event


def location_type_filter_ui():
	for location_type in LocationType:
		(ui.chip(text=location_type.keyword, icon=location_type.icon, color='secondary', text_color='primary',
		         selectable=True).props('outline icon-selected=highlight_off')
		 .bind_selected(LOCATION_TYPE_FILTER.location_types[location_type.keyword])
	#	 .on_selection_change(call_refresh_filter_event())
		 )
		 
	
"""	return (ui.select(
		{location_type: location_type.keyword for location_type in LocationType}
		, label="Ort", value=[location_type for location_type in LocationType], multiple=True, clearable=True)
	        .on_value_change(call_refresh_filter_event).bind_value(LOCATION_TYPE_FILTER.state)
	        .classes("pl-3 w-full my-1")).props("outline behavior=menu dense hide-dropdown-icon color=secondary")
"""

class LocationTypeFilterController:
	
	def __init__(self):
		self.location_types = {}
		for location_type in LocationType:
			self.location_types[location_type.keyword] =  binding.BindableProperty()
	
	def apply_filter_to_statement(self, statement: Select):
		
		if len(self.location_types) > 0:
			for location_type, value in self.location_types.items():
				#print(location_type, str(value))
				if value is None:
					statement = statement.where(Location.type.keyword != location_type)
		
		return statement


LOCATION_TYPE_FILTER = LocationTypeFilterController()


class LocalLocationTypeFilterController:
	
	def apply_filter_to_statement(self, statement: Select):
		return statement.where(Location.type == LocationType.local)


LOCAL_LOCATION_TYPE_FILTER = LocalLocationTypeFilterController()

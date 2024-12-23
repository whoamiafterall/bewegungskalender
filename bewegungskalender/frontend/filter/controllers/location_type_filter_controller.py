import math

from nicegui import binding
from sqlalchemy import Select, and_, or_

from bewegungskalender.backend.calendar.location import Location, EventLocationType
from bewegungskalender.frontend.helpers.controllers.location_search_controller import LocationSearchController

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
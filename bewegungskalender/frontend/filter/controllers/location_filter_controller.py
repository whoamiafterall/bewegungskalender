import math

from nicegui import binding
from sqlalchemy import Select, and_, or_

from bewegungskalender.backend.calendar.location import Location, EventLocationType
from bewegungskalender.frontend.helpers.controllers.location_search_controller import LocationSearchController


class LocationFilterController:

    def __init__(self):
        self.state = "Überall"
        self.force_offline = False
        self.location = LocationSearchController()
        self.distance = binding.BindableProperty()

    @property
    def usable_state(self):
        return "Offline" if self.force_offline else self.state

    def apply_filter_to_statement(self,statement: Select):
        # location filtering

        if self.usable_state == "Online":
            statement = statement.where(Location.type == EventLocationType.online)
        elif self.location.result is not None:
            distance = self.distance.value

            lat = float(self.location.result["lat"])
            lon = float(self.location.result["lon"])

            max_lat = lat + distance / 110.574
            min_lat = lat - distance / 110.574
            max_lon = lon + distance / 111.320 * math.cos(max_lat * math.pi / 180)
            min_lon = lon - distance / 111.320 * math.cos(min_lat * math.pi / 180)

            operation = and_(
                Location.lat > float(min_lat),
                Location.lat < float(max_lat),
                Location.lon > float(min_lon),
                Location.lon < float(max_lon),
            )
            if self.usable_state == "Offline":
                statement = statement.where(operation)
            else:
                statement = statement.where(or_(Location.type != EventLocationType.offline, operation))

        elif self.usable_state == "Offline":
            statement = statement.where(Location.type == EventLocationType.offline)
        return statement

LOCATION_FILTER = LocationFilterController()
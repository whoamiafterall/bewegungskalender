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

            distance_sq = (distance*distance)

            mod_lat_sq = float(math.pow(110.574,2))
            mod_lon_sq = float(math.pow(111.320 * math.cos(lat * math.pi / 180),2))

            distance_operation = (((Location.lat - float(lat)) * (Location.lat - float(lat)) * mod_lat_sq)
                             + ((Location.lon - float(lon)) * (Location.lon - float(lon)) * mod_lon_sq)
                             < distance_sq)

            if self.usable_state == "Offline":
                statement = statement.where(distance_operation)
            else:
                statement = statement.where(or_(Location.type != EventLocationType.offline, distance_operation))

        elif self.usable_state == "Offline":
            statement = statement.where(Location.type == EventLocationType.offline)
        return statement

LOCATION_FILTER = LocationFilterController()
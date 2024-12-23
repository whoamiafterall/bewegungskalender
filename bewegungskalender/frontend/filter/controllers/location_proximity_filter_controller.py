import math

from nicegui import binding
from sqlalchemy import Select, and_, or_

from bewegungskalender.backend.calendar.location import Location, EventLocationType
from bewegungskalender.frontend.helpers.controllers.location_search_controller import LocationSearchController


class LocationProximityFilterController:

    def __init__(self):
        self.location = LocationSearchController()
        self.distance = binding.BindableProperty()

    def apply_filter_to_statement(self,statement: Select):
        if self.location.result is not None:
            distance = self.distance.value

            lat = float(self.location.result["lat"])
            lon = float(self.location.result["lon"])

            distance_sq = (distance * distance)

            modifier_lat_sq = float(math.pow(110.574, 2))
            modifier_lon_sq = float(math.pow(111.320 * math.cos(lat * math.pi / 180), 2))

            return statement.where(
                or_(
                    # only apply filter if Event ist offline EventLocationType
                    Location.type != EventLocationType.offline,
                    # Distance calculation sr(lat1-lat2) * modifier + sr(lon1-lon2) * modifier
                    ((Location.lat - float(lat)) * (Location.lat - float(lat)) * modifier_lat_sq)
                    + ((Location.lon - float(lon)) * (Location.lon - float(lon)) * modifier_lon_sq)
                    < distance_sq
                )
            )
        else:
            return statement

LOCATION_PROXIMITY_FILTER = LocationProximityFilterController()
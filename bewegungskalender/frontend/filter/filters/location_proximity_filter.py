import math

from nicegui import ui, binding
from nicegui.element import Element
from sqlalchemy import Select, or_

from bewegungskalender.backend.calendar.location import Location, EventLocationType
from bewegungskalender.frontend.filter.filter import call_refresh_filter_event
from bewegungskalender.libs.exceptions import NoResultError
from bewegungskalender.libs.nominatim import search_city

class LocationSearchController:

    def __init__(self):
        self.search_query = ""
        self.search_result = None

    @property
    def query(self):
        return self.search_query

    @query.setter
    def query(self, new_value):
        self.search_query = new_value
        if self.search_query is None or self.search_query == "":
            self.search_result = None


    def update_search_result(self):
        if self.search_query is None:
            self.search_result = None
        else:
            try:
                self.search_result = search_city(self.search_query)[0]
            except NoResultError:
                self.search_result = None

    @property
    def result(self):
        return self.search_result


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
                    # Only apply filter if Event is local
                    Location.type != EventLocationType.local,
                    # Distance calculation sr(lat1-lat2) * modifier + sr(lon1-lon2) * modifier
                    ((Location.lat - float(lat)) * (Location.lat - float(lat)) * modifier_lat_sq)
                    + ((Location.lon - float(lon)) * (Location.lon - float(lon)) * modifier_lon_sq)
                    < distance_sq
                )
            )
        else:
            return statement

LOCATION_PROXIMITY_FILTER = LocationProximityFilterController()

def location_proximity_filter_ui() -> Element:
    holder = ui.list().classes("w-full")
    with holder:
        ui.input(label="🔎 Ort suchen", placeholder="Stadt").on('update:model-value', lambda: (
        LOCATION_PROXIMITY_FILTER.location.update_search_result(), call_refresh_filter_event()),
                                                               throttle=1.0, leading_events=False).bind_value(
            LOCATION_PROXIMITY_FILTER.location, "query").props('clearable filled').classes('w-full my-1 pl-3')

        with ui.card().classes("ml-3 gap-0.5 bg-primary text-secondary w-full max-w-[260px] no-shadow").bind_visibility_from(
                LOCATION_PROXIMITY_FILTER.location, 'result', lambda v: v is not None):
            ui.label("").bind_text_from(LOCATION_PROXIMITY_FILTER.location, 'result',
                                        backward=lambda a: "" if a is None else a["display_name"])



            ui.label("").bind_text_from(LOCATION_PROXIMITY_FILTER.distance, 'value',
                                        backward=lambda a: f"Radius: {a}km")

            ui.slider(min=1, max=10, step=0.25, value=1).on_value_change(call_refresh_filter_event).bind_value(
                LOCATION_PROXIMITY_FILTER.distance, backward=lambda i: math.sqrt(i / 10),
                forward=lambda i: round(i * i * 10)).props('thumb-color=accent selection-color=accent')

    return holder





import re
from typing import Optional, Tuple, TYPE_CHECKING

from geopy.geocoders.nominatim import Nominatim
from sqlmodel import SQLModel, Field, Relationship

from bewegungskalender.backend.io.config import LOCALE
from bewegungskalender.libs.exceptions import NoResultError
from bewegungskalender.libs.logger import LOGGER
from bewegungskalender.libs.nominatim import lookup_entity

if TYPE_CHECKING: # Necessary for SQLModel Relationships across Files
    from bewegungskalender.backend.calendar.event import Event

# Regular expression to match OSM links
OSM_ENTITY_LINK:re.Pattern = re.compile(r"(https?://www.openstreetmap.org/(way|node|relation)/\d{4,15})")

class Location(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    name: str
    event: "Event" = Relationship(back_populates="location") #TODO use list of events or id
    lat: float | None = None
    lon: float | None = None

def lookup_osm_link(result: str) -> Optional[Tuple[float, float]]:
    lon, lat = None, None
    # Assume result is a list of items, we process the first one
    if isinstance(result, list) and len(result) > 0:
        for key, value in result[0].items():
            if key == 'lon':
                lon = float(value)
            elif key == 'lat':
                lat = float(value)
    # Return coordinates as a tuple
    if lon is not None and lat is not None:
        return lon, lat
    else:
        return None

def get_location_data(location:str) -> Location:
    match location:
        case None:  # Filter events without location
            return Location(name='nicht bekannt')
        case "Online" | "online":  # Filter events with online/Online as location
            return Location(name='online')
        case link if OSM_ENTITY_LINK.match(link): # Check if location matches a link to an OSM-Entity
            try:
                result = lookup_entity(link)
            except NoResultError:
                return Location(name='nicht bekannt')
        case _: # Geocode location otherwise
            try:
                result = Nominatim(user_agent=__name__).geocode(location, language=LOCALE).raw
            except AttributeError: # No result found
                LOGGER.warning(NoResultError(location))
                return Location(name=location)
    return Location(name=location, lat=result['lat'], lon=result['lon'])
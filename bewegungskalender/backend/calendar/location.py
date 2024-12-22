import enum
import re
from typing import TYPE_CHECKING

from geopy.exc import GeocoderUnavailable
from geopy.geocoders.nominatim import Nominatim
from retry import retry
from sqlmodel import SQLModel, Field, Relationship

from bewegungskalender.backend.calendar.helper import get_link, try_get_link
from bewegungskalender.backend.io.config import LOCALE
from bewegungskalender.libs.exceptions import NoResultError
from bewegungskalender.libs.logger import LOGGER
from bewegungskalender.libs.nominatim import lookup_entity

if TYPE_CHECKING: # Necessary for SQLModel Relationships across Files
    from bewegungskalender.backend.calendar.event import Event

# Regular expression to match OSM links
OSM_LINK_PATTERN:re.Pattern = re.compile(r"(https?://www.openstreetmap.org/(way|node|relation)/\d{4,15})")
OSM_LINK:str = "https://www.openstreetmap.org"

class EventLocationType(str, enum.Enum):
    online = "online"
    offline = "offline"
    undefined = "undefined"

class Location(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    name: str | None = None
    event: "Event" = Relationship(back_populates="location",  sa_relationship_kwargs={"lazy": "selectin"}) #TODO use list of events or id
    type: EventLocationType = EventLocationType.undefined
    osm_link: str | None = None
    online_link: str | None = None
    lat: float | None = None
    lon: float | None = None
    city: str | None = None
    country: str | None = None
    country_code: str | None = None
    
    @classmethod
    def parse_offline(cls, result, location):
        return Location(type=EventLocationType.offline,
                        name=location,
                        lat=result['lat'],
                        lon=result['lon'],
                        osm_link=f"{OSM_LINK}/{result['osm_type']}/{result['osm_id']}",
                        city=_catch_key_error(result, 'city'),
                        country=_catch_key_error(result, 'country'),
                        country_code=_catch_key_error(result, 'country_code'))

    @classmethod
    def parse_online(cls, result):
        return Location(type=EventLocationType.online,
                        name=result,
                        online_link=result)

@retry(exceptions=GeocoderUnavailable, delay=2, max_delay=8, backoff=2)
def geocode(location:str) -> Location:
    try:
        # Find offline events
        result = Nominatim(user_agent=__name__).geocode(location, addressdetails=True, language=LOCALE).raw
        return Location.parse_offline(result, location)
    except AttributeError:  # No offline events found
        LOGGER.warning(NoResultError(location))
        return Location(name=location)
    
def _catch_key_error(result, key) -> str|None:
    try:
        return str(result['address'][key])
    except KeyError:
        return None

def get_location_data(location:str) -> Location:

    if location is None:  # Filter events without location
        return Location()
    elif OSM_LINK_PATTERN.match(location):
        # Try to find osm link
        try:
            result = lookup_entity(location)
            return Location.parse_offline(result, location)
        except NoResultError:
            LOGGER.warning(NoResultError(location))
            return Location()
    else:
        # Try to find online link
        location_get_link_result = get_link(location)
        if location_get_link_result is not None:
            return Location.parse_online(location_get_link_result)
        else:
            # Fallback geocode code
            return geocode(location)


   
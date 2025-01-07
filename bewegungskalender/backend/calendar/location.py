import re
from enum import StrEnum
from typing import TYPE_CHECKING

from geopy.exc import GeocoderUnavailable
from geopy.geocoders.nominatim import Nominatim
from retry import retry
from sqlmodel import SQLModel, Field, Relationship

from bewegungskalender.backend.formatting.format import get_link
from bewegungskalender.libs.exceptions import NoResultError
from bewegungskalender.libs.logger import LOGGER
from bewegungskalender.libs.nominatim import lookup_entity

if TYPE_CHECKING: # Necessary for SQLModel Relationships across Files
    from bewegungskalender.backend.calendar.event import Event

# Regular expression to match OSM links
OSM_LINK_PATTERN:re.Pattern = re.compile(r"(https?://www.openstreetmap.org/(way|node|relation)/\d{4,15})")
OSM_LINK:str = "https://www.openstreetmap.org"

class EventLocationType(StrEnum):
    online = "online"
    offline = "offline"
    undefined = "undefined"
    local = "local"
    national = "national"
    worldwide = "worldwide"

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
    def parse_local(cls, result, location):
        return Location(type=EventLocationType.local,
                        name=location,
                        lat=result['lat'],
                        lon=result['lon'],
                        osm_link=f"{OSM_LINK}/{result['osm_type']}/{result['osm_id']}",
                        city=_catch_key_error(result, 'city'),
                        country=_catch_key_error(result, 'country'),
                        country_code=_catch_key_error(result, 'country_code'))

def _catch_key_error(result, key) -> str|None:
    try:
        return str(result['address'][key])
    except KeyError:
        return None


@retry(exceptions=GeocoderUnavailable, delay=2, max_delay=8, backoff=2)
def parse_location(location: str | None) -> Location:
     # (has to be done before matching)
    if location is None:
        return Location(type=EventLocationType.undefined)
        
    # If there is a link to OpenStreetMap open it and parse coordinates
    # (has to be done before checking for other links)
    if OSM_LINK_PATTERN.match(location):
        try:
            result = lookup_entity(location)
            return Location.parse_local(result, location)
        except NoResultError:
            LOGGER.warning(NoResultError(location))
    
    # Try to find online link (e.g. to a Videocall)
    online_link = get_link(location)
    if online_link is not None:
        return Location(type=EventLocationType.online, name="Online", online_link=online_link)
 
     # Match the location to some cases
    match location.lower():
        case "online":
            return Location(type=EventLocationType.online, name="Online")
        case "global"|"weltweit"|"international":
            return Location(type=EventLocationType.worldwide, name="Weltweit")
        case "bundesweit"|"deutschland":
            return Location(type=EventLocationType.national, name="Bundesweit")
        
        case _:
            try:
                result = Nominatim(user_agent=__name__).geocode(location, addressdetails=True, language='de').raw
                return Location.parse_local(result, location)
            except AttributeError:  # No offline events found
                LOGGER.warning(NoResultError(location))
                return Location(name=location)
   


   
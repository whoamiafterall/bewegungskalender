import re
from time import sleep
from typing import Optional, Tuple, TYPE_CHECKING

from geopy.exc import GeocoderUnavailable
from geopy.geocoders.nominatim import Nominatim
from sqlmodel import SQLModel, Field, Relationship

from bewegungskalender.backend.io.config import LOCALE
from bewegungskalender.libs.exceptions import NoResultError, NetworkConnectionError
from bewegungskalender.libs.logger import LOGGER
from bewegungskalender.libs.nominatim import lookup_entity

if TYPE_CHECKING: # Necessary for SQLModel Relationships across Files
    from bewegungskalender.backend.calendar.event import Event

# Regular expression to match OSM links
OSM_LINK_PATTERN:re.Pattern = re.compile(r"(https?://www.openstreetmap.org/(way|node|relation)/\d{4,15})")
OSM_LINK:str = "https://www.openstreetmap.org"

class Location(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    name: str | None = None
    event: "Event" = Relationship(back_populates="location",  sa_relationship_kwargs={"lazy": "selectin"}) #TODO use list of events or id
    osm_link: str | None = None
    lat: float | None = None
    lon: float | None = None
    city: str | None = None
    country: str | None = None
    country_code: str | None = None
    
    @classmethod
    def parse(cls, result, location):
        return Location(name=location,
                        lat=result['lat'],
                        lon=result['lon'],
                        osm_link=f"{OSM_LINK}/{result['osm_type']}/{result['osm_id']}",
                        city=_catch_key_error(result, 'city'),
                        country=_catch_key_error(result, 'country'),
                        country_code=_catch_key_error(result, 'country_code'))
    
def geocode(location:str, retries:int = 3, seconds_to_wait:int = 30) -> Location:
    for attempt in range(retries):
        try:
            result = Nominatim(user_agent=__name__).geocode(location, addressdetails=True, language=LOCALE).raw
            return Location.parse(result, location)
        except AttributeError:  # No result found
            LOGGER.warning(NoResultError(location))
            return Location(name=location)
        except GeocoderUnavailable:
            LOGGER.info(
                f"\n\nCouldn't connect to {Nominatim.__name__} to look up {location}. "
                f"\nPlease check your network Connection and wait for the script to retry! "
                f"\nAttempts left: {retries - attempt - 1} ")
            for seconds_waited in range(seconds_to_wait):
                print(f"Retrying in {seconds_to_wait - seconds_waited} seconds...")
                sleep(1)
            continue
    else:
        raise NetworkConnectionError(Nominatim.__name__)
    
def _catch_key_error(result, key):
    try:
        return str(result['address'][key])
    except KeyError:
        return None

def get_location_data(location:str) -> Location:
    match location:
        case None:  # Filter events without location
            return Location()
        case "Online" | "online":  # Filter events with online/Online as location
            return Location(name=location.lower())
        case link if OSM_LINK_PATTERN.match(link): # Check if location matches a link to an OSM-Entity
            try:
                result = lookup_entity(link)
                return Location.parse(result, location)
            except NoResultError:
                LOGGER.warning(NoResultError(location))
                return Location()
        case _: # Geocode location otherwise
            return geocode(location)


   
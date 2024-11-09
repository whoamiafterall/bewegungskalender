import re
import urllib.parse
import codecs
import json
from typing import Tuple

from geojson import Feature, FeatureCollection
from slugify import slugify

from bewegungskalender.backend.calendar.category import Category
from bewegungskalender.backend.calendar.event import Event
from bewegungskalender.backend.formatting.format import Format
from bewegungskalender.libs.nominatim import Nominatim
from bewegungskalender.backend.io.config import MAPDATA_CACHE, LOCATION_CACHE
from bewegungskalender.libs.logger import LOGGER
from bewegungskalender.libs.datetime import event_time
from bewegungskalender.backend.formatting.formatting import add_link
from bewegungskalender.backend.io.file import safe_open

class MyPoint:
     def __init__(self, lon, lat):
        self.lon = lon
        self.lat = lat

     @property
     def __geo_interface__(self):
         return {'type': 'Point', 'coordinates': (self.lon, self.lat)}

def encode(location: str):
    try: str(codecs.encode(location, encoding='ascii', errors='strict'))
    except UnicodeEncodeError: 
        location = str(urllib.parse.quote(location))
    return location

def location_lookup(location: str) -> list|None:
    nominatim = Nominatim()
    # Check if there is a link to an OSM-Node/Relation/Way
    osm_link = re.search("(https?:\/\/openstreetmap.org/(way|node|relation)\/\d{4,15})", location)
    if osm_link is not None: # If yes, lookup this OSM-Link and get coordinates
        split = osm_link[0].rsplit('/', 2)
        return nominatim.lookup(split[-2].upper()[0] + split[-1])
    else: # If there is no OSM-Link try to search for the given location
        return nominatim.search(location, limit=1)

def get_cached_coordinates(path: str):
    f = open(path, "r")
    return json.loads(f.read())["coordinates"]

def cache_coordinates(path:str, location:str, coordinates:Tuple[float, float]):
    # Cache Coordinates
    with safe_open(path,"w") as f:
        f.write(json.dumps({
            "location": location,
            "coordinates": coordinates
        }))

# method that uses cached lon lat locations
def get_coordinates(location: str) -> Tuple[float, float]|None:
    # Check if location is None - else look it up through Nominatim
    result = None if location is None else location_lookup(location)
    if result is None or result == []: # If its None return None
        LOGGER.warning(f"no Result found for {location}")
        return None
    else: # Parse result, cache it and return it
        for key, value in result[0].items():
            match key:
                case 'lon':
                    lon = float(value)
                case 'lat':
                    lat = float(value)
        coordinates =  [lon, lat]
        LOGGER.debug(f"found {location}: {coordinates[0]}, {coordinates[1]}")
        return coordinates


def read_mapdata() -> list:
    with open(f"{MAPDATA_CACHE}", "r") as f:
        return json.loads(f.read())


def filter_events(event:Event) -> bool:
    location: str = event.location
    match location:
        case None:  # filter events without location
            LOGGER.debug(f"N: {event.summary}: location is None"); return True
        case "Online" | "online":  # filter events with online/Online as location
            LOGGER.debug(f"O: {event.summary}: location is Online"); return True
    return False

def create_mapdata(data: list[Category]) -> None:
    featureCollections:list = []
    for category in data:
        features:list = []
        recurrence:list = []
        LOGGER.debug(f"Creating Map Data for {category.name}...")
        for event in category.events:
            if filter_events(event):
                continue
            try: 
                recurrence.index(event.summary) # check if recurring event has already been located (Throws Value Error if not)
                if event.recurrence is not None:  # add recurring event to list for the check above
                    recurrence.append(event.summary)
                LOGGER.debug(f"{event.summary}: Skipping recurring event..."); continue
            except ValueError: # Event is not present in recurrence List
                path = f"{LOCATION_CACHE}/{slugify(event.location)}.json"
                try: # Try to find a file with cached coordinates
                    coordinates = get_cached_coordinates(path)
                except FileNotFoundError:
                    LOGGER.debug(f"Couldn't find cached coordinates for {event.location} - Looking online...")
                    coordinates = get_coordinates(event.location)
                if coordinates is not None:
                    cache_coordinates(path, event.location, coordinates)
                    feature = Feature(
                        geometry=MyPoint(coordinates[0], coordinates[1]),
                        properties={
                            'summary': event.summary,
                            'event_time': event_time(event.start, event.end),
                            'location': event.location,
                            'link': add_link(event.summary, event.description, Format.HTML)})
                    features.append(feature)

        LOGGER.info(f"Located {len(features)} Events from {category.name} on OpenStreetMap!")
                    
        # save some extra info in featureCollection to use for displaying leaflet later
        featureCollection = FeatureCollection(features)
        featureCollection["name"] = category.name
        featureCollection["map_marker"] = category.map_marker

        featureCollections.append(featureCollection)

    with safe_open(f"{MAPDATA_CACHE}", "w") as f: # write Data to file
        f.write(json.dumps(featureCollections))


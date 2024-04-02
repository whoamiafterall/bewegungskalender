from collections import namedtuple
import urllib.parse
import codecs
import logging
from nominatim import Nominatim
from geojson import Feature, FeatureCollection
from bewegungskalender.helper.formatting import search_link, eventtime, to_filename

nominatim = Nominatim()

class MyPoint():
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
    
def createFeature(event: namedtuple) -> MyPoint:
    location = event.location
    result = nominatim.query(query=encode(location), limit=1)
    if result == []:
        logging.info(f"R: {event.summary}: no Result found for {location}")
        return None
    for key, value in result[0].items():
        if key == 'lon':
            lon = float(value)
        if key == 'lat':
            lat = float(value)
    if lat is not None:
        logging.debug(f"{location} is here: {lon}, {lat}")
        return Feature(geometry=MyPoint(lon, lat), properties={'ℹ️': event.summary, 
                                               '📅': eventtime(event.start, event.end), 
                                               '📌': event.location, 
                                               '🌐': search_link(event.description)})
    return None

def createMapData(data: list, localdir: str):
    for calendar in data:
        features = []
        logging.debug(f"Creating Map Data for {calendar.name}...")
        for event in calendar.events:
            location = event.location
            if location is None:
                logging.info(f"N: {event.summary}: location is None"); continue
            if location == "Online" or location == "online":
                logging.debug(f"O: {event.summary}: location is Online"); continue
            features.append(createFeature(event))
        filename = f"{localdir}/{to_filename(calendar.name)}.geojson"
        logging.debug(f"Writing Map Data to File {filename}...")
        with open(filename, "w") as f:
                f.write(f"{FeatureCollection(features)}")
    return


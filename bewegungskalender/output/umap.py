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
    
def createPoint(location: str) -> MyPoint:
    result = nominatim.query(query=encode(location), limit=1)
    if result == []:
        print(f"R: {location}: no Result found")
        return None
    for key, value in result[0].items():
        if key == 'lon':
            lon = float(value)
        if key == 'lat':
            lat = float(value)
    if lat is not None:
        return MyPoint(lon, lat)
    return None

def createFeature(point: MyPoint, event: dict) -> Feature:
    return Feature(geometry=point, properties={'ℹ️': event['summary'], 
                                               '📅': eventtime(event['start'], event['end']), 
                                               '📌': event['location'], 
                                               '🌐': search_link(event['description'])})

def createMapData(data: list):
    for calendar in data:
        features = []
        logging.debug(f"Creating Map Data for {calendar.name}...")
        for event in calendar.events:
            location = event['location']
            if location is None:
                continue
            if location == "Online" or "online":
                continue
            features.append(createFeature(createPoint(location), event))
        logging.debug(f"Writing Map Data to File {to_filename(calendar.name)}...")
        with open(f"bewegungskalender/mapData/{to_filename(calendar.name)}.geojson", "w") as f:
            f.write(f"{FeatureCollection(features)}")
    return


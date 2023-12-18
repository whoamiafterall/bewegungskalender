import urllib.parse
import codecs
from nominatim import Nominatim
from geojson import Feature, FeatureCollection
from post_caldav_events.output.message import eventtime, link

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
    return Feature(geometry=point, properties={'ℹ️': event['summary'], '📅': eventtime(event['start'], event['end']), '📌': event['location'], '🌐': link(event['description'])})

def createMapData(events: dict):
    for calendar_name, event_list in events.items():
        print(); print(calendar_name)
        features = []
        for event in event_list:
            location = event['location']
            if location is None:
                print(f"N: {event['summary']}: location is None"); continue
            features.append(createFeature(createPoint(location), event))
        with open(f"post_caldav_events/mapData/{calendar_name}.geojson", "w") as f:
            f.write(f"{FeatureCollection(features)}")
    return


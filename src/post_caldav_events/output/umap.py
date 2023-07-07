import urllib.parse
import codecs
from nominatim import Nominatim, NominatimReverse
from geojson import Feature, Point, FeatureCollection

nominatim = Nominatim()

def encode(location: str):
    try: str(codecs.encode(location, encoding='ascii', errors='strict'))
    except UnicodeEncodeError: 
        location = str(urllib.parse.quote(location))
    return location
    
def getCoords(location: str) -> list:
    if location == "online" or location == "Online":
        return None
    if location is not None:
        result = nominatim.query(query=encode(location), limit=1)
    else:
        return None
    if result == []:
        print(location)
        return None
    coords = []
    for key, value in result[0].items():
        if key == 'lat':
            coords.append(float(value))
        if key == 'lon':
            coords.append(float(value))
    return coords

def createFeature(coords: list, event) -> Feature:
    properties = {'Name': f"[[{event['description']}|{event['summary']}]]"}
    return Feature(geometry=Point(coords), properties=properties)

def createMapData(events: dict):
    for calendar_name, event_list in events.items():
        if calendar_name == "Jahres & Gedenktage":
            continue
        if event_list == []:
            continue
        features = []
        for event in event_list:
            location = event['location']
            if location is None:
                print(f"{event['summary']} \n location is None")
            coords = getCoords(location)
            if coords is not None:
                features.append(createFeature(coords, event))
        with open(f"post_caldav_events/mapData/{calendar_name}.geojson", "w") as f:
            f.write(f"{FeatureCollection(features,)}")
    return

'''
[{u'boundingbox': [u'51.5162200927734',
   u'51.516357421875',
   u'-0.120491504669189',
   u'-0.12029179930687'],
  u'class': u'place',
  u'display_name': u'58, Parker Street, Holborn, St Giles, London Borough of Camden, London, Greater London, England, WC2, United Kingdom',
  u'importance': 0.421,
  u'lat': u'51.5162894',
  u'licence': u'Data \xa9 OpenStreetMap contributors, ODbL 1.0. http://www.openstreetmap.org/copyright',
  u'lon': u'-0.120392595530143',
  u'osm_id': u'148391190',
  u'osm_type': u'way',
  u'place_id': u'83887926',
  u'type': u'house'}]
''' 
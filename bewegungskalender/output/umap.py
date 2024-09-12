import re
from typing import NamedTuple
import urllib.parse
import codecs
import logging
import json
import base64
from bewegungskalender.helper.nominatim import NominatimSearch, NominatimLookup
from bewegungskalender.helper.formatting import search_link, eventtime, to_filename
from geojson import Feature, FeatureCollection
from functools import reduce
from slugify import slugify

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
  
# method that uses catched lon lat locations
def getCoordinateLocation(location: str,locationcatchdir:str):
    fname = f"{locationcatchdir}/{ slugify(location)}"
    try:
        f = open(fname, 'r')
        return json.loads(f.read())
    except:
        logging.debug(f"Could not open/read file for {location} Looking up location online ...") 

    coordinates = nominatimCoordinate(location)

    with open(f"{fname}", "w") as f:
        f.write(json.dumps(coordinates))      

    if coordinates == None:
        logging.warn(f"no Result found for {location}")
        return None

    logging.debug(f"found {location}: {coordinates[0]}, {coordinates[1]}")
    return coordinates

def nominatimCoordinate(location: str):

    result = nominatim(location)

    if result == []:
        return None

    # parse lat and lon
    for key, value in result[0].items():
        if key == 'lon':
            lon = float(value)
        if key == 'lat':
            lat = float(value)

    return [lon,lat]


def nominatim(location: str) -> list: #TODO test this 
    # query Nominatim and log if nothing is found
    loookup = NominatimLookup()
    # Check if there is a link to a OSM-Node/Relation/Way
    if location == "" or None:
        return None
    feature = re.search("(https?:\/\/openstreetmap.org\/(way|node|relation)\/\d{4,15})", location)
    if feature is not None: 
        split = feature.rsplit('/', 2)
        return loookup.query(split[-2].upper()[0] + split[-1]) # Lookup this OSM-Relation and get result

    #people often add things to adress at begining with open streetmap can't unterstand, for that reason we can remove portions of the string if location was not found until we find something of nothing left to remove
    return recursiveArraySearch(location.split(" "))


def recursiveArraySearch (locationArray):
    search = NominatimSearch()
    result = search.query(query=encode(reduce(lambda x, y: str(x) + " " + str(y), locationArray)), limit=1)
    if result == [] and len(locationArray) > 1:
        return recursiveArraySearch(locationArray[1:])
    return result

    
def createFeature(event: NamedTuple, locationcatchdir:str) -> MyPoint:
    
    coordinates = getCoordinateLocation(event.location,locationcatchdir)

    if coordinates == None:
        logging.warn(f"R: {event.summary}: {event.location} has no valid coordinates")
        return None

    return Feature(geometry=MyPoint(coordinates[0], coordinates[1]), properties={'summary': event.summary, 
                                            'eventtime': eventtime(event.start, event.end), 
                                            'location': event.location, 
                                            'link': search_link(event.summary, event.description)})
   
def readMapData(savedir:str) -> list: 
    with open(f"{savedir}", "r") as f:
        return json.loads(f.read())


def createMapData(data: list[NamedTuple], savedir:str, locationcatchdir:str) -> None: 
    featureCollections:list = []

    for calendar in data:
        features:list = []
        recurrence:list = []
        logging.debug(f"Creating Map Data for {calendar.name}...")
        for event in calendar.events:
            location:str = event.location
            if location is None: # filter events without location
                logging.debug(f"N: {event.summary}: location is None")
                search_link(event.summary, event.description) # call just for logs
                continue 
            if location == "Online" or location == "online": # filter events with online/Online as location
                logging.debug(f"O: {event.summary}: location is Online")
                search_link(event.summary, event.description) #call just for logs
                continue
            try: 
                recurrence.index(event.summary) # check if recurring event has already been located
                logging.debug(f"{event.summary}: Skipping recurring event...")
                continue
            except ValueError: # Event is not present in recurrence List
                feature = createFeature(event,locationcatchdir) # locate the event on OpenStreetMap
            if event.recurrence is not None: # add recurring event to list for the check above
                recurrence.append(event.summary)
            if feature is not None: # add located events to list 
                features.append(feature) 

        logging.info(f"Located {len(features)} Events from {calendar.name} on OpenStreetMap!")
                    
        #save some extra info in featureCollection to use for displaying map later
        featureCollection = FeatureCollection(features)
        featureCollection["name"] = calendar.name
        featureCollection["map_marker_url"] = calendar.map_marker_url

        featureCollections.append(featureCollection)

    with open(f"{savedir}", "w") as f: # write Data to file
        f.write(json.dumps(featureCollections))


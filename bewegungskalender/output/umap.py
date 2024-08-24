import re
from typing import NamedTuple
import urllib.parse
import codecs
import logging
from bewegungskalender.helper.nominatim import NominatimSearch, NominatimLookup
from geojson import Feature, FeatureCollection
from bewegungskalender.helper.formatting import search_link, eventtime, to_filename

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
  
def nominatim(location: str) -> list: #TODO test this 
    # query Nominatim and log if nothing is found
    search = NominatimSearch()
    loookup = NominatimLookup()
    # Check if there is a link to a OSM-Node/Relation/Way
    if location == "" or None:
        return None
    feature = re.search("(https?:\/\/openstreetmap.org\/(way|node|relation)\/\d{4,15})", location)
    if feature is not None: 
        split = feature.rsplit('/', 2)
        return loookup.query(split[-2].upper()[0] + split[-1]) # Lookup this OSM-Relation and get result
    return search.query(query=encode(location), limit=1)
    
def createFeature(event: NamedTuple) -> MyPoint:
    result = nominatim(event.location)
    if result == []:
        logging.warn(f"R: {event.summary}: no Result found for {event.location}")
        return None
    
    # parse results to GeoJSON
    for key, value in result[0].items():
        if key == 'lon':
            lon = float(value)
        if key == 'lat':
            lat = float(value)
    logging.debug(f"{event.summary}: found {event.location}: {lon}, {lat}")
    return Feature(geometry=MyPoint(lon, lat), properties={'ℹ️': event.summary, 
                                            '📅': eventtime(event.start, event.end), 
                                            '📌': event.location, 
                                            '🌐': search_link(event.summary, event.description)})
   

def createMapData(data: list[NamedTuple], localdir:str) -> None:    
    filenames:list = []
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
                feature = createFeature(event) # locate the event on OpenStreetMap
            if event.recurrence is not None: # add recurring event to list for the check above
                recurrence.append(event.summary)
            if feature is not None: # add located events to list 
                features.append(feature) 
        filename = f"{to_filename(calendar.name)}.geojson"
        logging.info(f"Located {len(features)} Events from {calendar.name} on OpenStreetMap!")
        filenames.append(filename)
        logging.debug(f"Writing to {filename}...")
        with open(f"{localdir}/{filename}", "w") as f: # write GeoJSON Data to each Calendar-File
            f.write(f"{FeatureCollection(features)}")
    return


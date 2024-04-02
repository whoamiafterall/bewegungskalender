from collections import namedtuple
import os
import urllib.parse
import codecs
import logging
from nominatim import Nominatim
import git
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
    
def createFeature(event: namedtuple) -> MyPoint:
    # query Nominatim and log if nothing is found
    location = event.location
    nominatim = Nominatim()
    result = nominatim.query(query=encode(location), limit=1)
    if result == []:
        logging.info(f"R: {event.summary}: no Result found for {location}")
        return None
    
    # parse results to GeoJSON
    for key, value in result[0].items():
        if key == 'lon':
            lon = float(value)
        if key == 'lat':
            lat = float(value)

    logging.debug(f"{location} is here: {lon}, {lat}")
    return Feature(geometry=MyPoint(lon, lat), properties={'ℹ️': event.summary, 
                                            '📅': eventtime(event.start, event.end), 
                                            '📌': event.location, 
                                            '🌐': search_link(event.description)})
   

def createMapData(data: list, localdir: str, remote: str):
    # Initialize and configure git repository if necessary
    if os.path.isdir(s=f"{localdir}/.git") == True: # if git repository already exists
        repo = git.Repo(path=localdir)  
        origin = repo.remote(name='master')
        logging.info(f"Found git repo in {localdir}!")
    else: 
        try: # Clone git repository from remote or initialize in if localdir already exists
            repo = git.Repo.clone_from(url=remote, to_path=localdir)
            origin = repo.create_remote(name='master', url=remote)   
            logging.info(f"Sucess! Cloned git repository from {remote} to {localdir}!")          
        except git.GitCommandError: 
            repo = git.Repo.init(path=localdir)
            origin = repo.create_remote(name='master', url=remote)    
            logging.info(f"Found git repo in {localdir} and added {remote} as 'master'!")
    # Parse 
    filenames = []
    for calendar in data:
        features = []
        logging.debug(f"Creating Map Data for {calendar.name}...")
        for event in calendar.events:
            location = event.location
            if location is None:
                logging.info(f"N: {event.summary}: location is None"); continue
            if location == "Online" or location == "online":
                logging.debug(f"O: {event.summary}: location is Online"); continue
            feature = createFeature(event) 
            if feature is not None:
                features.append(feature)
        filename = f"{to_filename(calendar.name)}.geojson"
        filenames.append(filename)
        logging.info(f"Writing Map Data to File {filename}...")
        with open(f"{localdir}/{filename}", "w") as f:
                f.write(f"{FeatureCollection(features)}")
    repo.index.add(filenames)
    repo.index.commit("Updated mapData")
    origin.push()
    logging.info(f"Success! Wrote GeoJSON Data to len{filenames} files and pushed them to {remote}!")
    return


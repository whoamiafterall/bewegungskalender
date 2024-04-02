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
        logging.warn(f"R: {event.summary}: no Result found for {location}")
        return None
    
    # parse results to GeoJSON
    for key, value in result[0].items():
        if key == 'lon':
            lon = float(value)
        if key == 'lat':
            lat = float(value)
    logging.debug(f"{event.summary}: found {location}: {lon}, {lat}")
    return Feature(geometry=MyPoint(lon, lat), properties={'ℹ️': event.summary, 
                                            '📅': eventtime(event.start, event.end), 
                                            '📌': event.location, 
                                            '🌐': search_link(event.summary, event.description)})
   

def createMapData(data: list, localdir: str, remote: str):
    # Initialize and configure git repository if necessary
    if os.path.isdir(s=f"{localdir}/.git") == True: # if git repository already exists in localdir
        repo = git.Repo(path=localdir)  
        origin = repo.remote(name='master')
        logging.debug(f"Using existing git repo in {localdir}...")
    else: # if git repository doesn't exist in localdir
        try: # try cloning git repository from remote repository
            repo = git.Repo.clone_from(url=remote, to_path=localdir)
            origin = repo.create_remote(name='master', url=remote)   
            logging.info(f"Sucessfully cloned git repository from {remote} to {localdir}!")          
        except git.GitCommandError: # except initialize it if localdir already exists
            repo = git.Repo.init(path=localdir)
            origin = repo.create_remote(name='master', url=remote)    
            logging.info(f"Found git repo in {localdir} and added {remote} as 'master'!")
    
    filenames = []
    for calendar in data:
        features = []
        recurrence = []
        logging.debug(f"Creating Map Data for {calendar.name}...")
        for event in calendar.events:
            location = event.location
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
    repo.index.add(filenames); repo.index.commit("Updated mapData"); origin.push() # Stage, Commit and Push Files to remote (origin)
    logging.info(f"Successfully pushed {len(filenames)} geojson files to {remote}!")
    return


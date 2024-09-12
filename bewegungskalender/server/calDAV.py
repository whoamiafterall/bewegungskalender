import datetime
from typing import NamedTuple

from caldav import Calendar, DAVClient
from nicegui import app
import requests
from bewegungskalender.helper.parsing import parse_event
from bewegungskalender.helper.logger import LOG
import caldav
import icalendar
from collections import namedtuple
    
def connect_davclient(config:dict):
    # Try to connect to CalDAV-Server
    LOG.info("Connecting to CalDav-Server using credentials from config...")
    try:
        with caldav.DAVClient(url=config['caldav']['url'], username=config['caldav']['username'], password=config['caldav']['password']) as client:
            return client    
    except ConnectionError:
        LOG.exception("Connection to CalDav-Server failed.")
        exit()
        
def search_events(config: dict, start: datetime.date, stop: datetime.date, expand=bool) -> list[NamedTuple] :
    # Connect to CalDAV Server
    data:list[NamedTuple] = []
    davclient:DAVClient = connect_davclient(config)
    LOG.info(f"Looking for Events between {start} and {stop} in {len(config['calendars'])} calendars... ")
    
    # Get Calendar Objects from Server
    for configline in config['calendars']:
        url = configline['calendar']['url']
        LOG.debug(f"Getting Data from {url}...")
        calobject:Calendar = davclient.calendar(url=url)
        
        # Search for Events this Calendar in the given timeframe and add them to a list
        events:list[NamedTuple] = []
        for cal_data in calobject.search(**{'start': start, 'end': stop}, event=True, expand=expand, sort_keys=['dtstart', 'summary']):
            for component in icalendar.Event.from_ical(cal_data.data).walk():
                if component.name == "VEVENT":
                    events.append(parse_event(component))
                    
        # Create Namedtuple to store Calendar Data in a useful way (Name, Emojis, Events, Map Marker)
        calendar:NamedTuple = namedtuple("calendar", ["emoji", "name", "events","map_marker"], defaults=[[]])
        try:
            calendar.name = calobject.get_properties([caldav.dav.DisplayName()])['{DAV:}displayname']
        except requests.ConnectionError:
            LOG.exception("Couldn't get calendar name from DAV-Client because of connection error. Aborting, please check your network connection and try again!")
            exit()
        calendar.events = events
        calendar.emoji = configline['calendar']['emoji']
        calendar.map_marker_url = configline['calendar']['map_marker_url']
        LOG.info(f"Successfully parsed {len(calendar.events)} events from {calendar.name}!")
        data.append(calendar)
    return data
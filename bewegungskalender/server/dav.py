import logging
from bewegungskalender.helper.parsing import parse_event
import caldav
import icalendar
from collections import namedtuple
    
def connect_davclient(config:dict):
    # Try to connect to CalDAV-Server
    logging.info("Connecting to CalDav-Server using credentials from config...")
    try:
        return caldav.DAVClient(url=config['caldav']['url'], username=config['caldav']['username'], password=config['caldav']['password'])    
    except ConnectionError:
        logging.exception("Connection to CalDav-Server failed.")
        exit()
        
def search_events(config: dict, start: int, stop: int) :
    # Connect to CalDAV Server
    data = []
    davclient = connect_davclient(config)
    logging.info(f"Looking for Events from {start} to {stop}")
    
    # Get Calendar Objects from Server
    for configline in config['calendars']:
        url = configline['calendar']['url']
        logging.debug(f"Getting Data from {url}...")
        calobject = davclient.calendar(url=url)
        
        # Search for Events this Calendar in the given timeframe and add them to a list
        events = []
        for cal_data in calobject.date_search(start, stop, "VEVENT"):
            for component in icalendar.Event.from_ical(cal_data.data).walk():
                if component.name == "VEVENT":
                    events.append(parse_event(component))
                    
        # Create Namedtuple to store Calendar Data in a useful way (Name, Emojis & Events)
        calendar = namedtuple("calendar", ["emoji", "name", "events"], defaults=[[]])
        try:
            calendar.name = calobject.get_properties([caldav.dav.DisplayName()])['{DAV:}displayname']
        except ConnectionError:
            calendar.name = url
        calendar.events = sorted(events, key=lambda e: e.start)
        calendar.emoji = configline['calendar']['emoji']
        logging.info(f"Successfully parsed {len(calendar.events)} events from {calendar.name}!")
        data.append(calendar)
    return data
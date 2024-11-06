from http.client import RemoteDisconnected

from requests.exceptions import ConnectionError
from caldav import Calendar, DAVClient
from bewegungskalender.classes.category import Category
from bewegungskalender.classes.event import Event
from bewegungskalender.functions.logger import LOGGER
from bewegungskalender.functions.config import CALENDARS, CALDAV_URL, CALDAV_PW, CALDAV_USR
from bewegungskalender.functions.cli import START, END
import caldav
import icalendar
        
def search_events() -> list[Category] :
    # Connect to CalDAV Server
    data:list[Category] = []
    davclient:DAVClient = caldav.DAVClient(url=CALDAV_URL, username=CALDAV_USR, password=CALDAV_PW)
    LOGGER.info(f"Looking for Events between {START} and {END} in {len(CALENDARS)} calendars... ")
    
    # Get Calendar Objects from Server
    for line in CALENDARS:
        url = line['calendar']['url']
        LOGGER.debug(f"Getting Data from {url}...")
        caldav_cal:Calendar = davclient.calendar(url=url)
        # Search for Events in this Calendar in the given timeframe and add them to a list
        events:list[Event] = []
        try:
            cal_data = caldav_cal.search(**{'start': START, 'end': END}, event=True, expand=True, sort_keys=['dtstart', 'summary'])
            name = caldav_cal.get_properties([caldav.dav.DisplayName()])['{DAV:}displayname']
        except ConnectionError or RemoteDisconnected:
            LOGGER.exception("Couldn't get data from CalDAV-Server because of connection error. Please check your network connection and try again!")
            return None and exit(1)
        for cal in cal_data:
            for component in icalendar.Event.from_ical(cal.data).walk():
                if component.name == "VEVENT":
                    events.append(Event.from_icalendar(component))
        calendar:Category = Category(
            name = name,
            events = events,
            emoji = line['calendar']['emoji'],
            map_marker = line['calendar']['map_marker'])
        LOGGER.info(f"Successfully parsed {len(calendar.events)} events from {calendar.name}!")
        data.append(calendar)
    return data
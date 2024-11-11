import functools
from datetime import datetime
from http.client import RemoteDisconnected

from caldav.davclient import Calendar, DAVClient
from caldav.elements.ical import CalendarColor
from caldav.objects import CalendarObjectResource
from requests.exceptions import ConnectionError

from bewegungskalender.backend.calendar.event import Event
from bewegungskalender.backend.io.cli import START, END
from bewegungskalender.backend.io.config import CALENDARS, CALDAV_URL, CALDAV_PW, CALDAV_USR
from bewegungskalender.libs.logger import LOGGER

# All Interactions with the CalDav Server are in this file
DAVCLIENT:DAVClient = DAVClient(url=CALDAV_URL, username=CALDAV_USR, password=CALDAV_PW)

def get_calendars() -> list[Calendar]:
    return DAVCLIENT.principal().calendars()

def get_calendar(url):
    LOGGER.debug(f"Getting Data from {url}...")
    return DAVCLIENT.calendar(url=url)

def get_calendar_name(cal:Calendar):
    return cal.get_display_name()

def get_calendar_color(cal:Calendar):
    return cal.get_property(CalendarColor(),True)

@functools.cache
def get_upcoming_events(cal:Calendar) -> list[Event]:
    LOGGER.info(f"Looking for Events between {datetime.date(START)} and {datetime.date(END)} in {len(CALENDARS)} calendars... ")
    # Search for Events in this Calendar in the given timeframe and add them to a list
    events:list[Event] = []
    try:
        cal_data:list[CalendarObjectResource] = cal.search(**{'start': START, 'end': END}, event=True, expand=True, sort_keys=['dtstart', 'summary'])
    except ConnectionError or RemoteDisconnected:
        LOGGER.exception("Couldn't get data from CalDAV-Server because of connection error. Please check your network connection and try again!")
        return None and exit(1)
    for ics in cal_data: # Basically a list of .ics links
        events.append(Event.from_icalendar(ics))
    return events


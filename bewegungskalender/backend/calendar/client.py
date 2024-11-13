from datetime import datetime
from functools import cache
from http.client import RemoteDisconnected

from caldav.davclient import Calendar, DAVClient
from caldav.elements.ical import CalendarColor
from caldav.objects import CalendarObjectResource
from requests.exceptions import ConnectionError

from bewegungskalender.backend.io.cli import START, END
from bewegungskalender.backend.io.config import CALDAV_URL, CALDAV_PW, CALDAV_USR
from bewegungskalender.libs.logger import LOGGER

# All Interactions with the CalDav Server are in this file
DAVCLIENT:DAVClient = DAVClient(url=CALDAV_URL, username=CALDAV_USR, password=CALDAV_PW)

def get_all_calendars() -> list[Calendar]:
    """Retrieve all calendars from the CalDAV server."""
    return DAVCLIENT.principal().calendars()

def get_calendar_by_url(url: str) -> Calendar:
    """Get a calendar by its URL."""
    LOGGER.debug(f"Getting data from {url}…")
    return DAVCLIENT.calendar(url=url)

def get_calendar_name(cal: Calendar) -> str:
    """Get the display name of a calendar."""
    return _catch_connection_error(lambda:cal.get_display_name())

def get_calendar_color(cal: Calendar) -> str:
    """Get the color property of a calendar."""
    return _catch_connection_error(lambda:cal.get_property(CalendarColor(), True))

def _catch_connection_error(func, *args):
    try:
        return func(*args)
    except (ConnectionError, RemoteDisconnected) as e:
        LOGGER.exception("Couldn't get data from CalDAV server due to connection error: %s", e)
        return None and exit(1)

@cache
def get_upcoming_events(cal:Calendar, start:datetime = START, end:datetime = END) -> list[CalendarObjectResource]:
    """Fetch upcoming events from a calendar within the given timerange.\n
    Sorts them by start-time and summary."""
    return _catch_connection_error(
        lambda:cal.search(**{'start': start, 'end': end}, event=True, expand=True,
                          sort_keys=['dtstart', 'summary']))


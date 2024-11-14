import sys
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

def _catch_connection_error(func, *args):
    """
    Executes a given function with the provided arguments, handling
    connection-related errors.

    This function attempts to call the specified function (`func`) with
    the supplied positional arguments (`*args`). If a `ConnectionError`
    or `RemoteDisconnected` exception is raised during the function call,
    it logs the error message and terminates the program with an
    exit status code of 1.

    Parameters:
    -----------
    func : callable
        The function to be executed.
    *args : tuple
        Positional arguments to be passed to the function.

    Returns:
    --------
    Any
        The return value of the executed function if no exceptions occur.

    Raises:
    -------
    SystemExit
        Exits the program when a connection error occurs.

    Example:
    --------
    result = _catch_connection_error(some_network_function, arg1, arg2)
    """
    try:
        return func(*args)
    except (ConnectionError, RemoteDisconnected) as e:
        LOGGER.exception("Couldn't get data from CalDAV server due to connection error: %s", e)
        sys.exit(1)  # Exit the program with code 1


def get_calendar_name(cal: Calendar) -> str:
    """Get the display name of a calendar."""
    return _catch_connection_error(lambda:cal.get_display_name())

def get_calendar_color(cal: Calendar) -> str:
    """Get the color property of a calendar."""
    return _catch_connection_error(lambda:cal.get_property(CalendarColor(), True))

@cache
def get_upcoming_events(cal:Calendar, start:datetime = START, end:datetime = END) -> list[CalendarObjectResource]:
    """Fetch upcoming events from a calendar within the given timerange.\n
    Sorts them by start-time and summary."""
    return _catch_connection_error(
        lambda:cal.search(**{'start': start, 'end': end}, event=True, expand=True,
                          sort_keys=['dtstart', 'summary']))


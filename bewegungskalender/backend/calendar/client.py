from datetime import datetime
from functools import cache
from http.client import RemoteDisconnected
from time import sleep

from caldav.davclient import Calendar, DAVClient
from caldav.elements.ical import CalendarColor
from caldav.objects import CalendarObjectResource
from requests import Timeout
from requests.exceptions import ConnectionError

from bewegungskalender.backend.io.cli import START, END
from bewegungskalender.backend.io.config import CALDAV_URL, CALDAV_PW, CALDAV_USR
from bewegungskalender.libs.exceptions import NetworkConnectionError
from bewegungskalender.libs.logger import LOGGER

# All Interactions with the CalDav Server are in this file
DAVCLIENT:DAVClient = DAVClient(url=CALDAV_URL, username=CALDAV_USR, password=CALDAV_PW)

def get_all_calendars() -> list[Calendar]:
    """Retrieve all calendars from the CalDAV server."""
    return DAVCLIENT.principal().calendars()

def get_calendar_by_url(url: str) -> Calendar:
    """Get a calendar by its URL."""
    LOGGER.info(f"Looking up {url}…")
    return DAVCLIENT.calendar(url=url)

def get_calendar_name(cal: Calendar) -> str:
    """Get the display name of a calendar."""
    LOGGER.debug("Getting name...")
    return _catch_connection_error(lambda:cal.get_display_name())

def get_calendar_color(cal: Calendar) -> str:
    """Get the color property of a calendar."""
    LOGGER.debug("Getting color...")
    return _catch_connection_error(lambda:cal.get_property(CalendarColor(), True))

@cache
def get_upcoming_events(cal:Calendar, start:datetime = START, end:datetime = END) -> list[CalendarObjectResource]:
    """Fetch upcoming events from a calendar within the given timerange.\n
    Sorts them by start-time and summary."""
    LOGGER.debug(f"Getting events between {start:%d.%m.} and {end:%d.%m.}...")
    return _catch_connection_error(
        lambda:cal.search(**{'start': start, 'end': end}, event=True, expand=True,
                          sort_keys=['dtstart', 'summary']))


def _catch_connection_error(func, retries:int = 3, seconds_to_wait:int = 30, *args:tuple, **kwargs:tuple):
    """
    Executes a given function with the provided arguments, handling
    connection-related errors.

    This function calls the specified function (`func`) with
    the supplied positional arguments (`*args`) and keyword arguments (`**kwargs`).

    If a `ConnectionError` or `RemoteDisconnected` exception is raised during the function call,
    it sleeps for (`seconds_to_wait = 30`) seconds and tries to connect again for (`retries = 3`) times.

    After failing on the last retry it raises a `NetworkConnectionError`.

    Parameters:
    -----------
    func : callable
        The function to be executed.
    retries : int
        The number of attempts to execute the function. Defaults to 3.
    seconds_to_wait : int
        The number of seconds to wait before retrying. Defaults to 30.
    *args : tuple
        Positional arguments to be passed to the function.
    **kwargs: tuple
        Keyword arguments to be passed to the function.

    Returns:
    --------
    Any
        The return value of the executed function if no exceptions occur.

    Raises:
    -------
    NetworkConnectionError
        Prints an Error message leading the user to check their Network connection.

    Example:
    --------
    result = _catch_connection_error(some_network_function, arg1, arg2)
    """
    for attempt in range(retries):
        try:
            result = func(*args, **kwargs)
        except (ConnectionError, RemoteDisconnected, Timeout):
            LOGGER.name = __name__
            LOGGER.info(f"\n\nCouldn't connect to {CALDAV_URL}. Please check your network Connection! "
                        f"\n\nRetrying in {seconds_to_wait} seconds..."
                        f"\nAttempts left: {retries - attempt - 1} ")
            sleep(seconds_to_wait)
            continue
        return result
    else:
        raise NetworkConnectionError(CALDAV_URL)
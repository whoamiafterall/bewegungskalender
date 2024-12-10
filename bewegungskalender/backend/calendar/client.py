from datetime import datetime
from functools import cache
from http.client import RemoteDisconnected
from time import sleep

from caldav import SynchronizableCalendarObjectCollection
from caldav.davclient import Calendar, DAVClient
from caldav.elements.dav import SyncToken
from caldav.elements.ical import CalendarColor
from caldav.objects import CalendarObjectResource
from requests import Timeout
from requests.exceptions import ConnectionError

from bewegungskalender.backend.io.cli import START, END
from bewegungskalender.backend.io.credentials import NC_DOMAIN, NC_PW, NC_USR
from bewegungskalender.libs.exceptions import NetworkConnectionError
from bewegungskalender.libs.logger import LOGGER

# All Interactions with the CalDav Server are in this file
DAVCLIENT:DAVClient = DAVClient(url=f"https://{NC_DOMAIN}/remote.php/dav/calendars", username=NC_USR, password=NC_PW)

def get_all_calendars() -> list[Calendar]:
	"""Retrieve all calendars from the CalDAV server."""
	return DAVCLIENT.principal().calendars()

def get_calendar_by_url(url: str) -> Calendar:
	"""Get a calendar by its URL."""
	LOGGER.debug(f"Looking up {url}…")
	return DAVCLIENT.calendar(url=f"{NC_USR}/{url}/")

def get_calendar_name(cal: Calendar) -> str:
	"""Get the display name of a calendar."""
	LOGGER.debug("Getting name...")
	return _catch_connection_error(lambda:cal.get_display_name())

def get_calendar_color(cal: Calendar) -> str:
	"""Get the color property of a calendar."""
	LOGGER.debug("Getting color...")
	return _catch_connection_error(lambda:cal.get_property(CalendarColor(), True))

def get_sync_token(cal:Calendar) -> SyncToken:
	LOGGER.debug("Getting sync_token...")
	return _catch_connection_error(lambda: cal.get_property(SyncToken(), use_cached=True))

def sync_all_events(cal:Calendar, sync_token:str) -> SynchronizableCalendarObjectCollection:
	LOGGER.info(f"Syncing {str(cal)}...")
	return _catch_connection_error(lambda: cal.objects_by_sync_token(sync_token, load_objects=True))

def get_all_events(cal:Calendar) -> SynchronizableCalendarObjectCollection:
	LOGGER.info(f"Getting all Events from {str(cal)}...")
	return _catch_connection_error(lambda: cal.objects(load_objects=True))

def get_upcoming_events(cal:Calendar, start:datetime = START, end:datetime = END) -> list[CalendarObjectResource]:
	"""Fetch upcoming events from a calendar within the given timerange.\n
	Sorts them by start-time and summary."""
	LOGGER.debug(f"Getting events from {str(cal)} between {start:%d.%m.} and {end:%d.%m.}...")
	return _catch_connection_error(
		lambda:cal.search(**{'start': start, 'end': end}, event=True, expand=True,
		                  sort_keys=['dtstart', 'summary']))


def _catch_connection_error(func, retries:int = 3, seconds_to_wait:int = 10, *args:tuple, **kwargs:tuple):
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
			LOGGER.info(f"\n\nCouldn't connect to {NC_DOMAIN}. Please check your network Connection and wait for the script to retry! "
			            f"\n\nRetrying in {seconds_to_wait} seconds..."
			            f"\nAttempts left: {retries - attempt - 1} ")
			for seconds_waited in range(seconds_to_wait):
				print(f"Retrying in {seconds_to_wait-seconds_waited} seconds...")
				sleep(1)
			continue
		return result
	else:
		raise NetworkConnectionError(NC_DOMAIN)
		
			
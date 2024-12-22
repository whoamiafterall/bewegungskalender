from datetime import datetime
from http.client import RemoteDisconnected

from caldav import SynchronizableCalendarObjectCollection
from caldav.davclient import Calendar, DAVClient
from caldav.elements.ical import CalendarColor
from caldav.objects import CalendarObjectResource
from requests import Timeout
from requests.exceptions import ConnectionError
from retry import retry

from bewegungskalender.backend.formatting.nextcloud_urls import NC_CALDAV_URL
from bewegungskalender.backend.io.cli import START, END
from bewegungskalender.backend.io.credentials import NC_PW, NC_USR
from bewegungskalender.libs.logger import LOGGER

# All Interactions with the CalDav Server are in this file
DAVCLIENT:DAVClient = DAVClient(url=NC_CALDAV_URL, username=NC_USR, password=NC_PW)

def get_all_calendars() -> list[Calendar]:
	"""Retrieve all calendars from the CalDAV server."""
	return DAVCLIENT.principal().calendars()

def get_calendar_by_url(url: str) -> Calendar:
	"""Get a calendar by its URL."""
	LOGGER.debug(f"Looking up {url}…")
	return DAVCLIENT.calendar(url=f"{NC_USR}/{url}/")

@retry(exceptions=(ConnectionError, RemoteDisconnected, Timeout), tries=5, delay=2, max_delay=32, backoff=2)
def get_calendar_name(cal: Calendar) -> str:
	"""Get the display name of a calendar."""
	LOGGER.debug("Getting name...")
	return cal.get_display_name()

@retry(exceptions=(ConnectionError, RemoteDisconnected, Timeout), tries=5, delay=2, max_delay=32, backoff=2)
def get_calendar_color(cal: Calendar) -> str:
	"""Get the color property of a calendar."""
	LOGGER.debug("Getting color...")
	return cal.get_property(CalendarColor(), True)

@retry(exceptions=(ConnectionError, RemoteDisconnected, Timeout), delay=2, max_delay=8, backoff=2)
def sync_all_events(cal:Calendar, sync_token:str) -> SynchronizableCalendarObjectCollection:
	LOGGER.info(f"Syncing {str(cal)}...")
	return cal.objects_by_sync_token(sync_token, load_objects=True)

@retry(exceptions=(ConnectionError, RemoteDisconnected, Timeout), delay=2, max_delay=8, backoff=2)
def get_all_events(cal:Calendar) -> SynchronizableCalendarObjectCollection:
	LOGGER.info(f"Getting all Events from {str(cal)}...")
	return cal.objects(load_objects=True)

@retry(exceptions=(ConnectionError, RemoteDisconnected, Timeout), delay=2, max_delay=8, backoff=2)
def get_upcoming_events(cal:Calendar, start:datetime = START, end:datetime = END) -> list[CalendarObjectResource]:
	"""Fetch upcoming events from a calendar within the given timerange.\n
	Sorts them by start-time and summary."""
	LOGGER.debug(f"Getting events from {str(cal)} between {start:%d.%m.} and {end:%d.%m.}...")
	return cal.search(**{'start': start, 'end': end}, event=True, expand=True,
		                  sort_keys=['dtstart', 'summary'])
			
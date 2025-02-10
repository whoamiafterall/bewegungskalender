import sys

import icalendar
from caldav.objects import CalendarObjectResource, Calendar, SynchronizableCalendarObjectCollection
from sqlmodel import SQLModel, Relationship, Field

from bewegungskalender.backend.calendar.client import get_calendar_by_url, get_calendar_name, get_calendar_color, \
	sync_all_events
from bewegungskalender.backend.calendar.event import Event
from bewegungskalender.backend.formatting.nextcloud_urls import get_ics_url
from bewegungskalender.libs.logger import LOGGER, log_status


# This is the Category Class used to categorize events
class Category(SQLModel, table=True):
	id: int = Field(default=None, primary_key=True)
	name: str
	internal: str
	public_id: str
	ics_url:str
	emoji: str
	color: str
	map_marker: str
	description: str
	sync_token: str|None = None
	events: list[Event] = Relationship(back_populates="category",
	                                   sa_relationship_kwargs={"lazy": "selectin"},
	                                   cascade_delete=True)
	
	@classmethod
	def create(cls, config_line:dict, calendar:Calendar):
		category = Category(
			name = get_calendar_name(calendar),
			internal = config_line['calendar']['internal'],
			public_id = config_line['calendar']['public'],
			ics_url = get_ics_url(config_line['calendar']['public']),
			emoji = config_line['calendar']['emoji'],
			color = get_calendar_color(calendar),
			map_marker = config_line['calendar']['map_marker'],
			description = config_line['calendar']['description'],
		)
		return category
	
	def sync(self) -> SynchronizableCalendarObjectCollection:
		# Get Calendar
		cal = get_calendar_by_url(self.internal)
		# Get Events that changed since last sync
		changed_events = sync_all_events(cal, self.sync_token)
		LOGGER.info(f"Syncing {self.sync_token} to {str(changed_events.sync_token)}")
		LOGGER.debug("|")
		return changed_events

	def update_events(self, cal_data: list[CalendarObjectResource]|SynchronizableCalendarObjectCollection, ref_status) -> list[Event]:
		LOGGER.info(f"Parsing events from {self.name}...")
		for counter, ics in enumerate(cal_data):
			log_status(ref_status, cal_data, counter)
			try:
				LOGGER.debug(f"Parsing {ics.icalendar_instance.subcomponents[0]['SUMMARY']}")
			except KeyError:
				LOGGER.critical(f"Summary cannot be None: {ics}\nPlease delete or adjust the event - otherwise this script will crash later!")
				sys.exit(1)
			for comp in icalendar.Event.from_ical(ics.data).walk(name='VEVENT'):
				self.events.append(Event().from_icalendar(comp, str(ics.url)))
		if isinstance(cal_data, SynchronizableCalendarObjectCollection):
			self.sync_token = cal_data.sync_token
		return self.events


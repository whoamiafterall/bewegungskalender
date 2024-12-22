import sys
import time

import icalendar
from caldav import SynchronizableCalendarObjectCollection
from caldav.objects import CalendarObjectResource
from sqlalchemy.exc import NoResultFound
from sqlalchemy.sql.functions import count
from sqlmodel import SQLModel, Relationship, Field, select
from starlette.config import undefined

from bewegungskalender.backend.calendar.client import get_calendar_by_url, get_calendar_name, get_calendar_color, \
	sync_all_events, get_all_events, get_upcoming_events
from bewegungskalender.backend.calendar.event import Event
from bewegungskalender.backend.formatting.nextcloud_urls import get_ics_url
from bewegungskalender.backend.io import db
from bewegungskalender.libs.logger import LOGGER


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
	def create(cls, full_db:bool, configline:dict,ref_status):
		cal = get_calendar_by_url(configline['calendar']['internal'])
		category = Category(
			name = get_calendar_name(cal),
			internal = configline['calendar']['internal'],
			public_id = configline['calendar']['public'],
			ics_url = get_ics_url(configline['calendar']['public']),
			emoji = configline['calendar']['emoji'],
			color = get_calendar_color(cal),
			map_marker = configline['calendar']['map_marker'],
			description = configline['calendar']['description'],
		)

		if full_db is False:
			category._update_events(get_upcoming_events(cal),ref_status)
		else:
			category._update_events(get_all_events(cal),ref_status)
		LOGGER.info(f"Found {len(category.events)} events in {category.name}!\nSaving to database...")
		with db.session() as sess:
			sess.add(category)
			sess.commit()
	
	def sync(self):
		cal = get_calendar_by_url(self.internal)
		updated_events = sync_all_events(cal, self.sync_token)



		print(f"Syncing {self.sync_token} to {str(updated_events.sync_token)}")
		print("|")
		for ics in updated_events:
			if ics.data is not None:
				# optain last sequence
				comp = undefined
				for temp_comp in icalendar.Event.from_ical(ics.data).walk(name='VEVENT'):
					comp = temp_comp

				#check if event is being deleted
				if "EXDATE" in comp:
					with db.session() as sess:
						event = sess.exec(select(Event).where(Event.ics_url == str(ics.url))).one()
						sess.delete(event)
						sess.commit()
					print(f"| deleted 1 Event")

				else:
					#for comp in icalendar.Event.from_ical(ics.data).walk(name='VEVENT'):
						#print(Event.from_icalendar(comp, str(comp['UID']), ics.url))
					#db.session().exec()
					try:
						with db.session() as sess:
							event = sess.exec(select(Event).where(Event.ics_url == str(ics.url))).one()
							event.update_from_icalendar(comp)
							sess.add(event)
							sess.commit()
							sess.refresh(event)
						print(f"| changed 1 Event")
					except NoResultFound:
						with db.session() as sess:
							category = sess.exec(select(Category).where(Category.id == self.id)).one()
							category.events.append(Event.from_icalendar(comp, str(comp['UID']), ics.url))
							sess.add(category)
							sess.commit()
							sess.refresh(category)
						print(f"| added 1 Event")


		print("--------------------")

		with db.session() as sess:
			category = sess.exec(select(Category).where(Category.id == self.id)).one()
			category.sync_token = str(updated_events.sync_token)
			sess.add(category)
			sess.commit()
			sess.refresh(category)

	def _update_events(self, cal_data: list[CalendarObjectResource]|SynchronizableCalendarObjectCollection, ref_status) -> list[Event]:
		LOGGER.info("Parsing events...")
		counter = 0
		for ics in cal_data:
			counter += 1
			exact_percent = 100 / ref_status['complete'] * ((ref_status['current']-1)+1 / len(cal_data) * counter)
			eta = "..." if exact_percent == 0 else round((time.time() - ref_status['start_time']) / exact_percent * (100 - exact_percent))

			LOGGER.info(f"Category [{ref_status['current']}/{ref_status['complete']}] Event [{counter}/{len(cal_data)}] - {round(exact_percent,1)}% ETA: {eta}s")


			try:
				LOGGER.debug(f"Parsing {ics.icalendar_instance.subcomponents[0]['SUMMARY']}")
			except KeyError:
				LOGGER.critical(f"Summary cannot be None: {ics}\nPlease delete or adjust the event - otherwise this script will crash later!")
				sys.exit(1)
			for comp in icalendar.Event.from_ical(ics.data).walk(name='VEVENT'):
				self.events.append(Event.from_icalendar(comp, str(comp['UID']), ics.url))
		if isinstance(cal_data, SynchronizableCalendarObjectCollection):
			self.sync_token = cal_data.sync_token
		return self.events

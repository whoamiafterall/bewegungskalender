from datetime import datetime, timedelta, time, date
from typing import TYPE_CHECKING, Optional

import icalendar
from icalendar.cal import Component
from icalendar.prop import vRecur
from sqlmodel import SQLModel, Field, Relationship

from bewegungskalender.backend.calendar.location import Location, parse_location
from bewegungskalender.backend.formatting.format import get_link
from bewegungskalender.backend.io.config import TIMEZONE

if TYPE_CHECKING:  # Necessary for SQLModel Relationships across Files
	from bewegungskalender.backend.calendar.category import Category


class Event(SQLModel, table=True):
	id: int = Field(default=None, primary_key=True)
	summary: str = Field(index=True)
	start: datetime = Field(index=True)
	end: datetime
	duration: timedelta = Field(index=True)
	category: "Category" = Relationship(back_populates="events", sa_relationship_kwargs={"lazy": "selectin"})
	category_id: int = Field(foreign_key="category.id", ondelete="CASCADE")
	description: str | None
	link: str | None
	location: Location = Relationship(back_populates="event", sa_relationship_kwargs={"lazy": "selectin"})
	location_id: int = Field(foreign_key="location.id")

	# Recurrence fields
	recurrence: bool = Field(default=False)
	recurrence_id: Optional[int] = None
	recurrence_rule_freq: Optional[str] = None
	recurrence_rule_interval: Optional[int] = None
	recurrence_rule_byday: Optional[str] = None  # e.g., 'MO,TU'
	recurrence_rule_bymonthday: Optional[str] = None  # e.g., '15'
	recurrence_rule_bymonth: Optional[str] = None  # e.g., '1,3,5'
	recurrence_rule_until: Optional[str] = None  # e.g., '20251231T000000Z'
	recurrence_rule_count: Optional[int] = None  # e.g., '10'
	recurrence_rule_bysetpos: Optional[str] = None  # e.g., '1'

	cloud_id: str = Field(index=True)
	ics_url: str
	
	def from_icalendar(self, vevent: Component, ics_url):
		# Make sure all the values are datetime not date in case of all day events
		def to_datetime(dt: date | datetime) -> datetime:
			if isinstance(dt, datetime):
				return dt
			return datetime.combine(dt, time.min).astimezone(TIMEZONE)
		
		start = to_datetime(vevent.decoded('dtstart'))
		end = to_datetime(vevent.decoded('dtend'))
		
		# Fix Issue with multi-day events by changing 'ends' midnight to 23:59:59 the day before instead of 00:00:00
		if start.date() != end.date() and end.time() == time.min:
			end = end - timedelta(seconds=1)
		
		self.summary = vevent.get('summary')
		self.link = get_link(vevent.get('description'))
		self.description = str(vevent.get('description')).replace(str(self.link), "")
		
		# TODO: prevent this from searching for locations twice by checking db first
		self.location = parse_location(vevent.get('location'))

		
		self.start = start
		self.end = end
		self.duration = end - start
		rrule = vevent.get('RRULE')
		if rrule:
			self.recurrence = True

			# Handle FREQ
			freq_value = rrule.get('FREQ')
			self.recurrence_rule_freq = freq_value[0] if isinstance(freq_value, list) else freq_value

			# Handle INTERVAL
			interval_value = rrule.get('INTERVAL')
			self.recurrence_rule_interval = int(interval_value[0]) if isinstance(interval_value, list) else int(
				interval_value) if interval_value else 1

			# Handle BYDAY
			byday_value = rrule.get('BYDAY', [])
			self.recurrence_rule_byday = ','.join(byday_value) if isinstance(byday_value, list) else byday_value

			# Handle BYMONTHDAY
			bymonthday_value = rrule.get('BYMONTHDAY', [])
			self.recurrence_rule_bymonthday = ','.join(map(str, bymonthday_value)) if isinstance(bymonthday_value,
																								 list) else bymonthday_value
			# Handle BYMONTH
			bymonth_value = rrule.get('BYMONTH', [])
			self.recurrence_rule_bymonth = ','.join(map(str, bymonth_value)) if isinstance(bymonth_value,
																						   list) else bymonth_value
			# Handle UNTIL
			until_value = rrule.get('UNTIL')
			self.recurrence_rule_until = until_value[0] if isinstance(until_value, list) else until_value

			# Handle COUNT
			count_value = rrule.get('COUNT')
			self.recurrence_rule_count = int(count_value[0]) if isinstance(count_value, list) and count_value else int(
				count_value) if count_value else None

			# Handle BYSETPOS
			bysetpos_value = rrule.get('BYSETPOS')
			self.recurrence_rule_bysetpos = bysetpos_value[0] if isinstance(bysetpos_value, list) else bysetpos_value

		self.cloud_id = vevent.get('UID')
		self.ics_url = str(ics_url)
		return self
	
	@classmethod
	def from_nextcloud_form(cls, row: dict[str, str]):
		"""
		Converts a row of data from the Nextcloud Form to an Event object.

		@param row: A row from the csv file containing the form data as dict.
		@return: An instance of the Event Class.
		"""
		
		# Handle Start of Event
		start_date = row['Start-Datum']
		start_time = row['Start-Zeit']
		
		if start_time != "":
			start = datetime.strptime(f"{start_date}-{start_time}", '%Y-%m-%d-%H:%M')
		else:  # When start-time is None return date
			start = datetime.strptime(start_date, '%Y-%m-%d')
		
		# Handle End of Event
		end_date = row['End-Datum']
		end_time = row['End-Uhrzeit']
		
		if end_date != "" and end_time != "":
			end = datetime.strptime(f"{end_date}-{end_time}", '%Y-%m-%d-%H:%M')
		elif end_date != "":  # When end-time is None return date
			end = datetime.strptime(end_date, '%Y-%m-%d')
		else:  # When both end-date and end-time are None return next day 00:00
			end = datetime.combine(start.date() + timedelta(1), datetime.min.time())
		
		event = Event(
			summary=f"{row['Titel']} ({row['Stadt/Region']})",
			location=row['Adresse'],
			description=f"{row['Beschreibung (lang)']}",
			link=f"{row['Link']}",
			start=start,
			end=end,
			recurrence=None,
			duration=end - start
		)
		return event
	
	def to_icalendar(self) -> icalendar.Event:
		event = icalendar.Event()
		event.add('summary', self.summary)
		event.add('description', self.link + self.description)
		event.add('location', self.location)
		event.add('dtstart', self.start)
		event.add('dtend', self.end)

		if self.recurrence:
			rrule = f"FREQ={self.recurrence_rule_freq};"
			if self.recurrence_rule_interval:
				rrule += f"INTERVAL={self.recurrence_rule_interval};"
			if self.recurrence_rule_byday:
				rrule += f"BYDAY={self.recurrence_rule_byday};"
			if self.recurrence_rule_bymonthday:
				rrule += f"BYMONTHDAY={self.recurrence_rule_bymonthday};"
			if self.recurrence_rule_bymonth:
				rrule += f"BYMONTH={self.recurrence_rule_bymonth};"
			if self.recurrence_rule_until:
				rrule += f"UNTIL={self.recurrence_rule_until};"
			if self.recurrence_rule_count:
				rrule += f"COUNT={self.recurrence_rule_count};"
			if self.recurrence_rule_bysetpos:
				rrule += f"BYSETPOS={self.recurrence_rule_bysetpos};"
			event.add('RRULE', rrule)

		return event

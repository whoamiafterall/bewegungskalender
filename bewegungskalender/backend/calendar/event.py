from datetime import datetime, timedelta, time, date
from typing import TYPE_CHECKING

import icalendar
from caldav.objects import URL
from icalendar.cal import Component
from sqlmodel import SQLModel, Field, Relationship

from bewegungskalender.backend.io.config import TIMEZONE
from bewegungskalender.backend.output.map_data import Location

if TYPE_CHECKING: # Necessary for SQLModel Relationships across Files
    from bewegungskalender.backend.calendar.category import Category

class Event(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    summary: str = Field()
    start: datetime = Field()
    end: datetime = Field()
    duration: timedelta = Field(index=True)
    category: "Category" = Relationship(back_populates="events")
    category_id: int = Field(foreign_key="category.id", ondelete="CASCADE")
    description: str | None = Field(default=None)
    location: "Location" = Relationship(back_populates="events")
    location_id: int = Field(foreign_key="location.id")
    recurrence: bool = False
    ics_url: str = None

    @classmethod
    def from_icalendar(cls, vevent: Component, ics_url:URL):
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

        # Create object
        event = Event(
            ics_url=str(ics_url),
            summary=vevent.get('summary'),
            description=vevent.get('description'),
            location=vevent.get('location'),
            start=start,
            end=end,
            duration=end-start,
            recurrence=True if vevent.get('recurrence-id') else False,
        )
        return event

    @classmethod
    def from_nextcloud_form(cls, row:dict[str,str]):
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

        if  end_date != "" and end_time != "":
            end = datetime.strptime(f"{end_date}-{end_time}", '%Y-%m-%d-%H:%M')
        elif end_date != "":  # When end-time is None return date
            end = datetime.strptime(end_date, '%Y-%m-%d')
        else:  # When both end-date and end-time are None return next day 00:00
            end = datetime.combine(start.date() + timedelta(1), datetime.min.time())

        event = Event(
            summary = f"{row['Titel']} ({row['Stadt/Region']})",
            location =  row['Adresse'],
            description = f"{row['Link']}\n{row['Beschreibung (lang)']}",
            start = start,
            end = end,
            recurrence = None,
            duration = end-start
        )
        return event

    def to_icalendar(self) -> icalendar.Event:
        event = icalendar.Event()
        event.add('summary', self.summary)
        event.add('description', self.description)
        event.add('location', self.location)
        event.add('dtstart', self.start)
        event.add('dtend', self.end)
        event.add('recurrence', self.recurrence)
        return event
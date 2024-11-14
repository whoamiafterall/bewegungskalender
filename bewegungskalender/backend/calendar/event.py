from datetime import datetime, timedelta
from typing import TYPE_CHECKING

import icalendar
from caldav.objects import URL
from icalendar.cal import Component
from sqlmodel import SQLModel, Field, Relationship

from bewegungskalender.libs.datetime import check_datetime, date_str, fix_midnight, calculate_duration
from bewegungskalender.libs.logger import LOGGER

if TYPE_CHECKING: # Necessary for SQLModel Relationships across Files
    from bewegungskalender.backend.calendar.category import Category

class Event(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    summary: str
    start: datetime
    end: datetime
    duration: timedelta = Field(index=True)
    category: "Category" = Relationship(back_populates="events")
    category_id: int = Field(foreign_key="category.id", ondelete="CASCADE")
    description: str | None = Field(default=None)
    location: str | None = Field(default=None)
    lat: float | None = None
    lon: float | None = None
    #bbox: list[float] | None = None
    recurrence: bool = False
    ics_url: str = None

    @classmethod
    def from_icalendar(cls, vevent: Component, ics_url:URL):
        start = check_datetime(vevent.decoded('dtstart'))
        end = check_datetime(vevent.decoded('dtend'))
        if date_str(start) != date_str(end):
            end = fix_midnight(end)
        event = Event(
            ics_url=str(ics_url),
            summary=vevent.get('summary'),
            description=vevent.get('description'),
            location=vevent.get('location'),
            start=start,
            end=end,
            duration=calculate_duration(start, end),
            recurrence=True if vevent.get('recurrence-id') else False,
        )
        LOGGER.debug(f"Success parsing {event.summary}...")
        return event

    @classmethod
    def from_nextcloud_form(cls, row:dict[str,str]):
        """
        Converts a row of data from the Nextcloud Form to an Event object.

        @param row: A row from the csv file containing the form data as dict.
        @return: An instance of the Event Class.
        """

        # Handle Start of Event
        if row['Start-Zeit'] != "":
            start = datetime.strptime(f"{row['Start-Datum']}-{row['Start-Zeit']}", '%Y-%m-%d-%H:%M')
        else:  # When start-time is None
            start = datetime.strptime(row['Start-Datum'], '%Y-%m-%d')

        # Handle End of Event
        if row['End-Datum'] != "" and row['End-Uhrzeit'] != "":
            end = datetime.strptime(f"{row['End-Datum']}-{row['End-Uhrzeit']}", '%Y-%m-%d-%H:%M')
        elif row['End-Datum'] != "":  # When end-time is None
            end = datetime.strptime(row['End-Datum'], '%Y-%m-%d')
        else:  # When both end-date and end-time are None
            end = datetime.combine(start.date() + timedelta(1), datetime.min.time())

        # Handle recurrence #TODO Fix this, add RRULE
        if row['Regelmäßig'] != "":
            match row['Regelmäßig']:
                case 'jährlich':
                    recurrence = False

        event = Event(
            summary = f"{row['Titel']} ({row['Stadt/Region']})",
            location =  row['Adresse'],
            description = f"{row['Link']}\n{row['Beschreibung (lang)']}",
            start = start,
            end = end,
            recurrence = recurrence, #TODO Fix
            duration = end-start, #TODO Test
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
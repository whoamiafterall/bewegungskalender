import orjson
import orjson as json
from dataclasses import dataclass, field
from datetime import datetime, timedelta

import icalendar
from validators import url
from caldav.objects import CalendarObjectResource

from bewegungskalender.libs.datetime import check_datetime, date_str, fix_midnight
from bewegungskalender.libs.logger import LOGGER

@dataclass
class Event:
    summary:str
    description:str
    location:str
    start:datetime
    end:datetime
    duration:timedelta
    recurrence:bool = field(default=False)
    url:url = field(default=None)

    @classmethod
    def from_icalendar(cls, event:CalendarObjectResource):
        for component in icalendar.Event.from_ical(event.data).walk():
            if component.name == "VEVENT":
                event = Event(
                    url = event.url,
                    summary = component.get('summary'),
                    description = component.get('description'),
                    location = component.get('location'),
                    start = check_datetime(component.decoded('dtstart')),
                    end = check_datetime(component.decoded('dtend')),
                    duration = event.get_duration(),
                    recurrence = True if component.get('recurrence-id') else False,
                )
        if date_str(event.start) != date_str(event.end):
            event.end = fix_midnight(event.end)

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
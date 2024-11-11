from datetime import datetime, timedelta

import icalendar
import validators
from caldav.objects import CalendarObjectResource

from bewegungskalender.libs.datetime import check_datetime, date_str, fix_midnight
from bewegungskalender.libs.logger import LOGGER


class Event:
    def __init__(self, summ: str, desc: str, loc: str, start: datetime, end: datetime, rec: str|None, dur:timedelta, url:validators.url = None):
        self.url:validators.url = url
        self.summary: str = summ
        self.description:str = desc
        self.location:str = loc
        self.start:datetime = start
        self.end:datetime = end
        self.duration:timedelta = dur
        self.recurrence:str|None = rec

    @classmethod
    def from_icalendar(cls, event:CalendarObjectResource):
        for component in icalendar.Event.from_ical(event.data).walk():
            if component.name == "VEVENT":
                event = Event(
                    url=event.url,
                    summ=component.get('summary'),
                    desc = component.get('description'),
                    loc=component.get('location'),
                    start = check_datetime(component.get('dtstart').dt),
                    end = check_datetime(component.get('dtend').dt),
                    dur= event.get_duration(),
                    rec = component.get('recurrence-id'),
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
                    recurrence = None

        event = Event(
            summ = f"{row['Titel']} ({row['Stadt/Region']})",
            loc =  row['Adresse'],
            desc = f"{row['Link']}\n{row['Beschreibung (lang)']}",
            start = start,
            end = end,
            rec = None, #TODO Fix
            dur = end-start, #TODO Test
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
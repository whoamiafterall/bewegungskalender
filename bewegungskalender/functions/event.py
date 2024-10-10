import icalendar
from docutils.nodes import description
from icalendar.cal import Component
from datetime import datetime, timedelta
from bewegungskalender.functions.datetime import check_datetime, date_str, fix_midnight
from bewegungskalender.functions.logger import LOGGER

class Event():
    def __init__(self, sum:str = None, desc:str = None, loc:str = None,
                 start:datetime = None, end:datetime = None, rec:str = None):
        self.summary: str = sum
        self.description:str = desc
        self.location:str = loc
        self.start:datetime = start
        self.end:datetime = end
        self.recurrence:str = rec
        pass

    @classmethod
    def from_icalendar(cls, component:Component):
        event = Event()
        event.summary = component.get('summary')
        event.description = component.get('description')
        event.location = component.get('location')
        event.start = check_datetime(component.get('dtstart').dt)
        event.end = check_datetime(component.get('dtend').dt)
        print(component.get('rrule'))
        event.recurrence = component.get('recurrence-id')

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
        event = Event()
        event.summary = f"{row['Titel']} ({row['Stadt/Region']})"
        event.location = 'location', row['Adresse']
        event.description = 'description', f"{row['Link']}\n{row['Beschreibung (lang)']}"

        # Handle Start of Event
        if row['Start-Zeit'] != "":
            event.start = datetime.strptime(f"{row['Start-Datum']}-{row['Start-Zeit']}", '%Y-%m-%d-%H:%M')
        else:  # When start-time is None
            event.start = datetime.strptime(row['Start-Datum'], '%Y-%m-%d')

        # Handle End of Event
        if row['End-Datum'] != "" and row['End-Uhrzeit'] != "":
            event.end = datetime.strptime(f"{row['End-Datum']}-{row['End-Uhrzeit']}", '%Y-%m-%d-%H:%M')
        elif row['End-Datum'] != "":  # When end-time is None
            event.end = datetime.strptime(row['End-Datum'], '%Y-%m-%d')
        else:  # When both end-date and end-time are None
            event.end = datetime.combine(event.start.date() + timedelta(1), datetime.min.time())

        # Handle recurrence
        if row ['Regelmäßig'] != "":
            match row['Regelmäßig']:
                case 'jährlich':
                    event.recurrence = None
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
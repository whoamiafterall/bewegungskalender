import orjson as json
from dataclasses import dataclass

from caldav import CalendarObjectResource
import icalendar

from bewegungskalender.backend.calendar.client import get_calendar_by_url, get_calendar_name, get_upcoming_events, \
    get_calendar_color
from bewegungskalender.backend.calendar.event import Event
from bewegungskalender.backend.io.config import CALENDAR_CACHE
from bewegungskalender.backend.io.file import safe_open
from bewegungskalender.libs.logger import LOGGER

# This is the Category Class used to categorize events
class Category():
    def __init__(self, configline:dict):
        cal = get_calendar_by_url(configline['calendar']['url'])
        self.name = get_calendar_name(cal)
        self.emoji = configline['calendar']['emoji']
        self.color = get_calendar_color(cal)
        self.map_marker = configline['calendar']['map_marker']
        self.events = self._from_caldav_search(get_upcoming_events(cal))
        LOGGER.name = self.name
        LOGGER.info(f"Found {len(self.events)} events!")

    def cache(self):
        with safe_open(f"{CALENDAR_CACHE}/{self.name}.json", "wb")as f:
            f.write(json.dumps(self, default=str))

    def _from_caldav_search(self, cal_data: list[CalendarObjectResource]) -> list[Event]:
        events = []
        for ics in cal_data:
            for comp in icalendar.Event.from_ical(ics.data).walk(name='VEVENT'):
                events.append(Event.from_icalendar(comp, ics.url, self.name))
        return events

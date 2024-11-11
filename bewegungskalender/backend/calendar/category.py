import orjson as json
from dataclasses import dataclass

from bewegungskalender.backend.calendar.client import get_calendar, get_calendar_name, get_upcoming_events, \
    get_calendar_color
from bewegungskalender.backend.io.config import CALENDAR_CACHE
from bewegungskalender.backend.io.file import safe_open
from bewegungskalender.libs.logger import LOGGER

# This is the Category Class used to categorize events
@dataclass
class Category():
    def __init__(self, configline:dict):
        cal = get_calendar(configline['calendar']['url'])
        self.name = get_calendar_name(cal)
        self.emoji = configline['calendar']['emoji']
        self.color = get_calendar_color(cal)
        self.map_marker = configline['calendar']['map_marker']
        self.events = get_upcoming_events(cal)
        LOGGER.info(f"Successfully got {len(self.events)} events from {self.name}! Caching...")
        self.cache()

    def cache(self):
        with safe_open(f"{CALENDAR_CACHE}/{self.name}.json", "wb")as f:
            f.write(json.dumps(self, default=str))

import json

from bewegungskalender.backend.calendar.client import get_calendar, get_calendar_name, get_upcoming_events, \
    get_calendar_color
from bewegungskalender.backend.io.config import CALENDAR_CACHE
from bewegungskalender.backend.io.file import safe_open
from bewegungskalender.libs.logger import LOGGER

# This is the Category Class used to categorize events
class Category:
    def __init__(self, configline:dict):
        self.cal = get_calendar(configline['calendar']['url'])
        self.name = get_calendar_name(self.cal)
        self.events = get_upcoming_events(self.cal)
        self.emoji = configline['calendar']['emoji']
        self.color = get_calendar_color(self.cal)
        self.map_marker = configline['calendar']['map_marker']
        LOGGER.info(f"Successfully got {len(self.events)} events from {self.name}!")

    def cache(self):
        with safe_open(f"{CALENDAR_CACHE}/{self.name}", "w")as f:
            f.write(json.dumps(self))

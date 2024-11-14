import icalendar
from caldav.objects import CalendarObjectResource
from sqlmodel import SQLModel, Relationship, Field

from bewegungskalender.backend.calendar.client import get_calendar_by_url, get_calendar_name, get_upcoming_events, \
    get_calendar_color
from bewegungskalender.backend.calendar.event import Event
from bewegungskalender.libs.logger import LOGGER


# This is the Category Class used to categorize events
class Category(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    name: str
    url: str
    emoji: str
    color: str
    map_marker: str
    events: list[Event] = Relationship(back_populates="category", cascade_delete=True)

    @classmethod
    def create(cls, configline:dict):
        cal = get_calendar_by_url(configline['calendar']['url'])
        category = Category(
            name = get_calendar_name(cal),
            url = cal.canonical_url,
            emoji = configline['calendar']['emoji'],
            color = get_calendar_color(cal),
            map_marker = configline['calendar']['map_marker'],
        )
        category._update_events(get_upcoming_events(cal))
        LOGGER.name = category.name
        LOGGER.info(f"Found {len(category.events)} events! Saving...")
        return category

    def _update_events(self, cal_data: list[CalendarObjectResource]) -> list[Event]:
        for ics in cal_data:
            for comp in icalendar.Event.from_ical(ics.data).walk(name='VEVENT'):
                self.events.append(Event.from_icalendar(comp, ics.url))
        return self.events

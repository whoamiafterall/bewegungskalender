import time
from collections.abc import Callable
from datetime import timedelta, datetime
from typing import Literal

import icalendar
import pytz
from caldav.objects import Calendar, CalendarObjectResource, SynchronizableCalendarObjectCollection
from dateutil.rrule import rrulestr
from icalendar.cal import Component
from sqlalchemy import Engine
from sqlalchemy.exc import NoResultFound, MultipleResultsFound
from sqlmodel import create_engine, SQLModel, Session, select, desc

from bewegungskalender.backend.calendar.category import Category
from bewegungskalender.backend.calendar.client import get_calendar_by_url
from bewegungskalender.backend.calendar.event import Event
from bewegungskalender.backend.calendar.event_instance import EventInstance
from bewegungskalender.backend.calendar.location import Location
from bewegungskalender.backend.io.cli import DB_MODE
from bewegungskalender.backend.io.config import DATADIR, SYNC_DB_FILE, SEARCH_DB_FILE, CALENDARS, TIMEZONE
from bewegungskalender.libs.exceptions import DatabaseError
from bewegungskalender.libs.nominatim import LOGGER


class DB:
    FIRST_EVENT: Event
    LAST_EVENT: Event
    _MODES = Literal["search", "sync", "full"]
    
    def __init__(self, mode_:_MODES = "full"):
        # Choose correct file depending on mode
        match mode_:
            case "search":
                _SQLITE_URL: str = f"sqlite:///{DATADIR}/{SEARCH_DB_FILE}"
            case "sync" | "full":
                _SQLITE_URL: str = f"sqlite:///{DATADIR}/{SYNC_DB_FILE}"
            case _:
                LOGGER.exception(f"{mode_} is not a valid Database type. Choose from: {self._MODES}")
                raise DatabaseError(mode_)
        self._ENGINE: Engine = create_engine(_SQLITE_URL)
    
    def create_tables(self) -> None:
        SQLModel.metadata.create_all(self._ENGINE)
        
    def drop_tables(self) -> None:
        SQLModel.metadata.drop_all(self._ENGINE)
    
    def exe(self, statement):
        with Session(self._ENGINE) as sess:
            return sess.exec(statement, execution_options={"prebuffer_rows": True})
    
    def dump(self): #TODO make this create a json File with db content
        return Session(self._ENGINE).exec(select(Event,Location,Category).join(Location).join(Category)).all()
    
    def add(self, instance:object):
        with Session(self._ENGINE) as sess:
            sess.add(instance)
            sess.commit()
            sess.refresh(instance)
    
    def delete(self, instance:object):
        with Session(self._ENGINE) as sess:
            sess.delete(instance)
            sess.commit()
            sess.refresh(instance)
            LOGGER.info(f"| deleted {repr(instance)}")
    
    def populate(self, func:Callable[[Calendar], list[CalendarObjectResource] | SynchronizableCalendarObjectCollection]):
        start_time = time.time()
        for counter, config_line in enumerate(CALENDARS):
            calendar = get_calendar_by_url(config_line['calendar']['internal'])
            category = Category.create(config_line, calendar)
            category.update_events(func(calendar), ref_status={'start_time': start_time, 'current': counter,
                                                                         'complete': len(CALENDARS)})
            LOGGER.info(f"Found {len(category.events)} events in {category.name}!\n")
            self.add(category)
        self.get_range()
            
    def get_range(self):
        try:
            self.FIRST_EVENT = self.exe(select(Event).order_by(Event.start)).first()
            self.LAST_EVENT = self.exe(select(Event).order_by(desc(Event.start))).first()
            LOGGER.info(f"The database contains events from: \n{self.FIRST_EVENT.start.date()} to \n{self.LAST_EVENT.end.date()}")
        except AttributeError:
            raise DatabaseError(f"get first and last event. Database seems to be empty!")
       # return self.FIRST_EVENT.start.date(), self.LAST_EVENT.end.date()

    def update_event_instances(self):
        with Session(self._ENGINE) as sess:

            for event in sess.exec(select(Event)).all():
                existing_instances = event.event_instances
                existing_start_times = {instance.start for instance in existing_instances}
                last_event_time:datetime = max((instance.start for instance in existing_instances), default=event.start).astimezone(pytz.utc)
                end_date = (event.start + timedelta(days=730)).astimezone(pytz.utc)  # 2 years

                if event.recurrence_rule:
                    rule = rrulestr(event.recurrence_rule, dtstart=last_event_time)

                    for occurrence in rule:
                        if occurrence < end_date:
                            if occurrence in existing_start_times:
                                instance = next(instance for instance in existing_instances if instance.start == occurrence)
                                instance.end = occurrence + event.duration
                            else:
                                event_instance = EventInstance(
                                    event=event,
                                    start=occurrence,
                                    end=occurrence + event.duration,
                                    duration=event.duration
                                )
                                sess.add(event_instance)
                                sess.commit()
                                sess.refresh(event_instance)
                        else:
                            break
                else:
                    if last_event_time in existing_start_times:
                        instance = next(instance for instance in existing_instances if instance.start == last_event_time)
                        instance.end = event.end
                    else:
                        event_instance = EventInstance(
                            event=event,
                            start=event.start,
                            end=event.end,
                            duration=event.duration
                        )
                        sess.add(event_instance)
                        sess.commit()
                        sess.refresh(event_instance)


    def update_events(self):
        if DB_MODE != "sync":
            raise DatabaseError(f"sync the database. Database of type {DB_MODE} cannot be synced!")
        for category in self.exe(select(Category)).all():
            changed_events = Category.sync(category)
            
            def compare_event(compo: Component): #TODO fix problem with recurring events
                print(str(compo.get('UID')))
                try:
                    return self.exe(select(Event).where(Event.cloud_id == str(compo.get('UID')))).one()
                except MultipleResultsFound:
                    raise MultipleResultsFound(f"Found multiple events with this cloud_id: {str(compo.get('UID'))}, corresponding to: {comp}.\n\nPlease repopulate your DB with -db full.")
            
            # For each changed event
            for ics in changed_events:
                if ics.data is None:
                    continue
                for comp in icalendar.Event.from_ical(ics.data).walk(name='VEVENT'):
                    LOGGER.info(Event().from_icalendar(comp, ics.url))
                    try: # Try to update the event in the database
                        event = compare_event(comp)
                        if "EXDATE" in comp:   # Check if event is being deleted
                            self.delete(event)
                        else: # If it changed in another way
                            event.from_icalendar(comp)
                            self.add(event)
                            LOGGER.info(f"| changed 1 Event")
                    except NoResultFound:  # Add the event if there is no such event in the database
                        category.events.append(Event().from_icalendar(comp, ics.url))
                        self.add(category)
                        LOGGER.info(f"| added 1 Event")
        
            LOGGER.info("--------------------")
            category.sync_token = str(changed_events.sync_token)
            self.add(category)
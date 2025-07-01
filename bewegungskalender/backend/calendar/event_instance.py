from datetime import datetime, timedelta, time, date
from typing import TYPE_CHECKING

import icalendar
from icalendar.cal import Component
from sqlmodel import SQLModel, Field, Relationship

from bewegungskalender.backend.calendar.location import Location, parse_location
from bewegungskalender.backend.formatting.format import get_link
from bewegungskalender.backend.io.config import TIMEZONE

if TYPE_CHECKING:  # Necessary for SQLModel Relationships across Files
	from bewegungskalender.backend.calendar.category import Category


class EventInstance(SQLModel, table=True):
	id: int = Field(default=None, primary_key=True)
	event: "Event" = Relationship(back_populates="event_instances",
								  sa_relationship_kwargs={"lazy": "selectin"})
	start: datetime = Field(index=True)
	end: datetime
	duration: timedelta = Field(index=True)
from datetime import datetime, timedelta, time, date
from typing import TYPE_CHECKING

from sqlmodel import SQLModel, Field, Relationship

if TYPE_CHECKING:  # Necessary for SQLModel Relationships across Files
	from bewegungskalender.backend.calendar.category import Category


class EventInstance(SQLModel, table=True):
	id: int = Field(default=None, primary_key=True)
	event: "Event" = Relationship(back_populates="event_instances",
								  sa_relationship_kwargs={"lazy": "selectin"})
	event_id: int = Field(foreign_key="event.id", ondelete="CASCADE")

	start: datetime = Field(index=True)
	end: datetime
	duration: timedelta = Field(index=True)
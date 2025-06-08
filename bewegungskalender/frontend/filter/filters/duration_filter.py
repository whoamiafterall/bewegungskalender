import enum
from datetime import timedelta

from nicegui import ui, binding
from nicegui.element import Element
from sqlalchemy import Select, and_, or_

from bewegungskalender.backend.calendar.event import Event
from bewegungskalender.frontend.filter.filter import call_refresh_filter_event


def duration_filter_ui() -> Element:
    return ((ui.select([duration_type.keyword for duration_type in DurationFilterType], value=DurationFilterType.All.keyword, label="Dauer",
        ).classes("pl-3 w-1/2 my-1"))
        .props("outline dense behavior=menu hide-dropdown-icon color=secondary").on_value_change(call_refresh_filter_event)
        .bind_value(DURATION_FILTER.duration))


class DurationFilterType(enum.Enum):
    #TODO Move this to backend so we can just check for a value in the db
    Hours = ('Kurz-Events (<8 Stunden)', None, timedelta(hours=8))
    OneDay = ('Ganz-Tages-Events', timedelta(hours=8), timedelta(hours=24))
    Days = ('Mehrtägige Events', timedelta(hours=24), None)
    All = ('Alle', None, None)

    def __init__(self, keyword, min_dur, max_dur):
        self.keyword = keyword
        self.min_dur = min_dur
        self.max_dur = max_dur
        

class DurationFilterController:
    def __init__(self):
        self.duration = binding.BindableProperty()
        self.duration.value = [DurationFilterType.All.keyword, DurationFilterType.Days.keyword,DurationFilterType.OneDay.keyword,DurationFilterType.Hours.keyword]

    def apply_filter_to_statement(self,statement: Select,recurring: bool):

        # duration filtering
        duration_args = []

        for duration_type in [e for e in DurationFilterType]:
            if duration_type.keyword in self.duration.value:
                if duration_type.min_dur is not None and duration_type.max_dur is not None:
                    duration_args.append(and_(Event.duration > duration_type.min_dur, Event.duration < duration_type.max_dur))
                elif duration_type.min_dur is None and duration_type.max_dur is not None:
                    duration_args.append(and_(Event.duration < duration_type.max_dur))
                elif duration_type.min_dur is not None and duration_type.max_dur is None:
                    duration_args.append(and_(Event.duration > duration_type.min_dur))

        if len(duration_args) == 1:
            return statement.where(duration_args[0])
        elif len(duration_args) > 1:
            return statement.where(or_(*duration_args))
        else:
            return statement


DURATION_FILTER = DurationFilterController()

import enum
from datetime import timedelta

from nicegui import ui, binding
from nicegui.element import Element
from sqlalchemy import Select, and_, or_

from bewegungskalender.backend.calendar.event import Event
from bewegungskalender.frontend.filter.filter import call_refresh_filter_event


def duration_filter_ui() -> Element:
	return (ui.select({DurationFilterType.Hours.keyword: 'Kurz'
            , DurationFilterType.OneDay.keyword: 'Ganztags'
            , DurationFilterType.Days.keyword: 'Mehrtägig'}, label="Dauer",
	           multiple=True, clearable=True).classes("pl-3 w-full my-1")).props("filled color=secondary").on_value_change(call_refresh_filter_event).bind_value(TIME_FILTER.duration)

class DurationFilterType(enum.Enum):

    Hours = ('Hours', None,timedelta(hours=6))
    OneDay = ('OneDay', timedelta(hours=6),timedelta(hours=36))
    Days = ('Days',timedelta(hours=24),None)

    def __init__(self, keyword, min_dur, max_dur):
        self.keyword = keyword
        self.min_dur = min_dur
        self.max_dur = max_dur

class TimeFilterController:
    def __init__(self):
        self.duration = binding.BindableProperty()
        self.duration.value = [DurationFilterType.Days.keyword,DurationFilterType.OneDay.keyword,DurationFilterType.Hours.keyword]

    def apply_filter_to_statement(self,statement: Select):

        # time filtering ----------------- (Comment this out to test with data from the past)
        # statement = statement.where(Event.start > today())

        # until = datetime.now().__add__(timedelta(days=100))
        # statement = statement.select(Event.start < until)

        # duration filtering
        duration_series = self.duration.value
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
            statement = statement.where(duration_args[0])
        elif len(duration_args) > 1:
            statement = statement.where(or_(*duration_args))

        return statement


TIME_FILTER = TimeFilterController()

from datetime import timedelta

from dateutil.utils import today
from nicegui import binding
from sqlalchemy import Select, and_, or_

from bewegungskalender.backend.calendar.event import Event


class TimeFilterController:
    def __init__(self):
        self.duration = binding.BindableProperty()

    def apply_filter_to_statement(self,statement: Select):

        # time filtering ----------------- (Comment this out to test with data from the past)
        statement = statement.where(Event.start > today())

        # until = datetime.now().__add__(timedelta(days=100))
        # statement = statement.select(Event.start < until)

        # duration filtering
        duration_series = self.duration.value
        duration_args = []

        if "Mehrtägig" in duration_series:
            duration_args.append(Event.duration > timedelta(hours=24))
        if "Ganztags" in duration_series:
            duration_args.append(and_(Event.duration > timedelta(hours=6), Event.duration < timedelta(hours=36)))
        if "Kurz" in duration_series:
            duration_args.append(Event.duration <= timedelta(hours=6))

        if len(duration_args) == 1:
            statement = statement.where(duration_args[0])
        elif len(duration_args) > 1:
            statement = statement.where(or_(*duration_args))

        return statement

TIME_FILTER = TimeFilterController()

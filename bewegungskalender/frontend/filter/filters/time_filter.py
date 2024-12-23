from datetime import timedelta

from nicegui import ui, binding
from nicegui.element import Element
from sqlalchemy import Select, and_, or_

from bewegungskalender.backend.calendar.event import Event
from bewegungskalender.frontend.filter.filter import call_refresh_filter_event

	
def duration_filter_ui() -> Element:
	return (ui.select(["Mehrtägig", "Ganztags", "Kurz"], label="Dauer", value=["Mehrtägig", "Ganztags", "Kurz"],
	           multiple=True, clearable=True).classes("pl-3 w-full my-1")).props("filled color=secondary").on_value_change(call_refresh_filter_event).bind_value(TIME_FILTER.duration)


class TimeFilterController:
    def __init__(self):
        self.duration = binding.BindableProperty()
        self.duration.value = ["Mehrtägig","Ganztags","Kurz"]

    def apply_filter_to_statement(self,statement: Select):

        # time filtering ----------------- (Comment this out to test with data from the past)
        # statement = statement.where(Event.start > today())

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

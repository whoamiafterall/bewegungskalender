import calendar
from datetime import datetime

from nicegui import ui, binding
from sqlalchemy import Select
from sqlmodel import or_, and_

from bewegungskalender.backend.calendar.event import Event
from bewegungskalender.frontend.filter.filter import call_refresh_filter_event


def month_filter_ui():
    with ui.button_group().classes('h-10 items-stretch'):

        months_list = {}
        for i in range(1, 13):
            months_list[i] = calendar.month_name[i]
        years_list = {}
        for i in range(datetime.now().year-1, datetime.now().year+1):
            years_list[i] = i

        ui.button(icon='navigate_before',on_click=TIME_FILTER.decrement_month).props('dense text-color=secondary')
        ui.select(options=months_list,
                ).props("dense behavior=menu color=secondary hide-dropdown-icon menu-offset=[10,10]"
                ).classes('font-medium grow bg-primary'
                ).bind_value(TIME_FILTER.month,
                ).on_value_change(call_refresh_filter_event)
        ui.button(icon='navigate_next', on_click=TIME_FILTER.increment_month).props('dense text-color=secondary')
        ui.select(options=years_list,
                ).props("dense behavior=menu color=secondary hide-dropdown-icon menu-offset=[10,10]"
                ).classes('font-medium pr-3 grow bg-primary rounded-r-sm'
                ).bind_value(TIME_FILTER.year,
                ).on_value_change(call_refresh_filter_event)


class TimeFilterController:
    def __init__(self):
        # Get first and last event in database so we know which months exist
        self.month = binding.BindableProperty()
        self.month.value = datetime.now().month

        self.year = binding.BindableProperty()

        self.year.value = datetime.now().year

    def decrement_month(self):
        if self.month.value > 1:
            self.month.value = self.month.value - 1
        else:
            self.month.value = 12
            self.year.value = self.year.value - 1

    def increment_month(self):
        if self.month.value < 12:
            self.month.value = self.month.value + 1
        else:
            self.month.value = 1
            self.year.value = self.year.value + 1
        # TODO implement a proper where statement
    def apply_filter_to_statement(self,statement: Select):
        month_begin = datetime(self.year.value, self.month.value,1)
        month_end = datetime(self.year.value, self.month.value+1,1) if self.month.value+1 <= 12 else datetime(self.year.value+1, 1,1)

        return statement.where(
            or_(and_(Event.start > month_begin,Event.start < month_end)
                ,and_(Event.end > month_begin,Event.end < month_end))
        )

TIME_FILTER = TimeFilterController()

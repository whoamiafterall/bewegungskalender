import locale
from datetime import datetime

from nicegui import ui, binding
from sqlalchemy import Select
from sqlmodel import select, desc

from bewegungskalender.backend.calendar.event import Event
from bewegungskalender.backend.io import db
from bewegungskalender.backend.io.config import LOCALE
from bewegungskalender.frontend.filter.filter import call_refresh_filter_event


def month_filter_ui():
    with ui.button_group().classes('h-10 items-stretch'):
        ui.button(icon='navigate_before')
        ui.select(options=TIME_FILTER.month.value, with_input=True,
                ).props("outline dense autocomplete behavior=menu color=secondary hide-dropdown-icon menu-offset=[10,10]"
                ).classes('font-medium grow'
                ).bind_value(TIME_FILTER.month,
                ).on_value_change(call_refresh_filter_event)
        ui.button(icon='navigate_next')

class TimeFilterController:
    def __init__(self):
        # Get first and last event in database so we know which months exist
        first_event = db.exe(select(Event).order_by(Event.start)).first()
        last_event =  db.exe(select(Event).order_by(desc(Event.start))).first()
        
        # Taken from https://stackoverflow.com/a/34898764 - creates a list of the months between first and last event
        total_months = lambda dt: dt.month + 12 * dt.year
        months = []
        locale.setlocale(locale.LC_ALL, LOCALE) # For whatever reason the following months are in English if locale is not set here
        for tot_m in range(total_months(first_event.start) - 1, total_months(last_event.end)):
            year, month = divmod(tot_m, 12)
            months.append(f"{datetime(year, month + 1, 1):%B %Y}")
    
        self.month = binding.BindableProperty()
        self.month.value = months
        
        # TODO implement a proper where statement
    def apply_filter_to_statement(self,statement: Select):
         return statement #statement.where(Event.start == self.month).where(Event.start == self.month)

TIME_FILTER = TimeFilterController()

from dateutil.utils import today
from nicegui import binding
from sqlalchemy import Select

from bewegungskalender.backend.calendar.event import Event


class TimeFilterController:

    def apply_filter_to_statement(self,statement: Select):
         return statement.where(Event.start > today())

TIME_FILTER = TimeFilterController()

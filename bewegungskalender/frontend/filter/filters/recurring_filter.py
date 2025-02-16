from nicegui import ui, binding
from sqlalchemy import Select

from bewegungskalender.backend.calendar.event import Event
from bewegungskalender.frontend.filter.filter import call_refresh_filter_event


def recurring_filter_ui():
	with ((ui.checkbox(text="Regelmäßige Events", value=True).classes('px-0'
                         ).props('color=secondary checked-icon=event_repeat unchecked-icon=close'
                         ).on_value_change(call_refresh_filter_event
                         ).bind_value(RECURRING_FILTER.show_recurring))):
				ui.tooltip("Hier kannst du regelmäßige Events filtern. Beachte, dass Jahrestage und Aktionstage teilweise jährlich eingetragen sind."
				    ).classes('text-balance text-sm font-medium text-center sm:w-[300px]'
				    ).props('delay=150 hide-delay=200')

class RecurringFilterController:
	def __init__(self):
		self.show_recurring = binding.BindableProperty()
		self.show_recurring.value = True
	
	def apply_filter_to_statement(self, statement: Select):
		if self.show_recurring.value is False:
			statement = statement.where(Event.recurrence == self.show_recurring.value)
		return statement

RECURRING_FILTER = RecurringFilterController()

import calendar
from datetime import datetime

from nicegui import ui, binding
from sqlalchemy import Select, extract, func, case
from sqlmodel import or_, and_

from bewegungskalender.backend.calendar.event import Event
from bewegungskalender.frontend.filter.filter import call_refresh_filter_event


def month_filter_ui():
	with ((ui.button_group().classes('h-10 items-stretch').props('dense flat'))):
		ui.button(icon='navigate_before', on_click=MONTH_FILTER.decrement_month
		          ).props('dense text-color=secondary')
		ui.select(options=MONTH_FILTER.months_list,
		          ).props("dense filled behavior=menu hide-dropdown-icon color=secondary menu-offset=[10,10]"
		                  ).classes('font-medium bg-primary'
		                            ).bind_value(MONTH_FILTER.month,
		                                         ).on_value_change(call_refresh_filter_event)
		ui.button(icon='navigate_next', on_click=MONTH_FILTER.increment_month
		          ).props('dense text-color=secondary')
		ui.select(options=MONTH_FILTER.years_list,
		          ).props("dense filled behavior=menu hide-dropdown-icon color=secondary menu-offset=[10,10]"
		                  ).classes('font-medium pr-3 rounded-r-sm bg-primary'
		                            ).bind_value(MONTH_FILTER.year,
		                                         ).on_value_change(call_refresh_filter_event)


class MonthFilterController:
	
	def __init__(self):
		# Get first and last event in database so we know which months exist
		self.month = binding.BindableProperty()
		self.month.value = datetime.now().month
		self.year = binding.BindableProperty()
		self.year.value = datetime.now().year
		self.months_list = {}
		for i in range(1, 13):
			self.months_list[i] = calendar.month_name[i]
		self.years_list = {}
		for i in range(datetime.now().year - 1, datetime.now().year + 1):
			self.years_list[i] = i
	
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
	

	def apply_filter_to_statement(self, statement: Select,recurring: bool):
		month_begin = datetime(self.year.value, self.month.value, 1)
		month_end = datetime(self.year.value, self.month.value + 1, 1) if self.month.value + 1 <= 12 else datetime(
			self.year.value + 1, 1, 1)




		return statement.where(
			and_(
				Event.recurrence == True,
				Event.start < month_end,
				or_(
					 Event.recurrence_rule_until == None,
					 Event.recurrence_rule_until > month_begin
				),
				or_(
					and_(
						Event.recurrence_rule_freq == "MONTHLY",
						func.mod(func.abs((self.year.value - extract('year', Event.start))*12+(self.month.value-extract('month', Event.start))),Event.recurrence_rule_interval) == 0
					),
					and_(
						Event.recurrence_rule_freq == "YEARLY",
						func.mod(func.abs(extract('year', Event.start) - self.year.value),Event.recurrence_rule_interval) == 0,self.month.value == extract('month', Event.start)
					),
					and_(
						Event.recurrence_rule_freq == "DAILY",
						func.mod(func.abs(func.julianday(Event.start) - func.julianday(month_begin)),Event.recurrence_rule_interval) < (month_end - month_begin).days
					)
				)
			) if recurring else and_(
				Event.recurrence == False,
				or_(and_(Event.start > month_begin, Event.start < month_end)
					, and_(Event.end > month_begin, Event.end < month_end))
			)
		)


MONTH_FILTER = MonthFilterController()


class FromTodayFilterController:
	
	def apply_filter_to_statement(self, statement: Select,recurring: bool):
		return statement if recurring else statement.where(Event.start > datetime.now())


FROM_TODAY_FILTER = FromTodayFilterController()

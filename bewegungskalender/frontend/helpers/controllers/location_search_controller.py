import sched
import time
import asyncio

from bewegungskalender.libs.exceptions import NoResultError
from bewegungskalender.libs.nominatim import search_city


class LocationSearchController:

	def __init__(self):
		self.event = None
		self.search_query = ""
		self.search_result = None
		self.scheduler = sched.scheduler(time.time, time.sleep)

	@property
	def query(self):
		return self.search_query

	@query.setter
	def query(self, new_value):
		self.search_query = new_value

		# Implemented as suggested here https://github.com/zauberzeug/nicegui/issues/1086 in order to prevent a UI event issue
		# Find event loop
		loop = asyncio.get_event_loop()
		# run in executor
		loop.run_in_executor(None,self.change_executer)

	# cancel old event, enqueue new and run
	def change_executer(self):
		if self.scheduler.queue.__contains__(self.event):
			self.scheduler.cancel(self.event)
			self.event = None
		if self.event is None or len(self.scheduler.queue) == 0:
			self.event = self.scheduler.enter(1, 1, self.run_search)
		self.scheduler.run()

	def run_search(self):
		if self.search_query is None:
			self.search_result = None
		else:
			try:
				self.search_result = search_city(self.search_query)[0]
			except NoResultError:
				self.search_result = None

	@property
	def result(self):
		return self.search_result
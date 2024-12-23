import sched
import time
import asyncio

from bewegungskalender.libs.exceptions import NoResultError
from bewegungskalender.libs.nominatim import search_city


class LocationSearchController:

	def __init__(self):
		self.search_query = ""
		self.search_result = None

	@property
	def query(self):
		return self.search_query

	@query.setter
	def query(self, new_value):
		self.search_query = new_value
		if self.search_query is None or self.search_query == "":
			self.search_result = None


	def update_search_result(self):
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
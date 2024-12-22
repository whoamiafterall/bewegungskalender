from nicegui import binding
from slugify import slugify
from sqlalchemy import select, Select

from bewegungskalender.backend.calendar.category import Category
from bewegungskalender.backend.io import db
from bewegungskalender.backend.io.config import CALENDARS

class CategoryFilterController:
    def __init__(self):
        self.categories = {}

        for calendar in CALENDARS:
            self.categories[f"{slugify(str(calendar['calendar']['internal']))}"] = binding.BindableProperty()

    def apply_filter_to_statement(self,statement: Select):
        for calendar in CALENDARS:
            if self.categories[f"{slugify(str(calendar['calendar']['internal']))}"].value is False:
                statement = statement.where(
                    Category.internal != calendar['calendar']['internal']
                )
        return statement

CATEGORY_FILTER = CategoryFilterController()
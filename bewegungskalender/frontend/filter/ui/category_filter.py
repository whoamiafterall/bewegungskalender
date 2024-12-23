from nicegui import ui
from nicegui.element import Element
from slugify import slugify
from sqlmodel import select

from bewegungskalender.backend.calendar.category import Category
from bewegungskalender.backend.io import db
from bewegungskalender.frontend.filter.controllers.category_filter_controller import CATEGORY_FILTER
from bewegungskalender.frontend.filter.filter import call_refresh_filter_event
from bewegungskalender.frontend.functions import mini_card, dropdown_button


async def categories_filters_ui() -> Element:
	holder = ui.list().classes("w-full")
	with holder:

		await ui.context.client.connected()
		categories = db.exe(select(Category)).all()

		# Create Buttons with useful Information and Links for each Category
		for category in categories:
			single_category_filter_ui(category)
					
	return holder

def single_category_filter_ui(category: Category):
	with mini_card('w-full py-0 px-0 m-0'):
		# Check Box
		with ui.checkbox(value=True).classes('px-0').on_value_change(call_refresh_filter_event).bind_value(
				CATEGORY_FILTER.categories[f"{slugify(str(category.internal))}"]):
			ui.tooltip(category.description).classes(
				'text-balance text-sm font-medium text-center sm:w-[300px]').style(
				f"background-color:{category.color}").props('delay=150 hide-delay=200')

		# Dropdown Button
		with dropdown_button(category.name, category.color):
			# Create the dropdown content
			with mini_card('space-x-2'):
				ui.button(text='Copy subscribe link', icon='content_copy',
						  on_click=lambda: ui.clipboard.write(category.ics_url)
						  ).props('flat color=white').classes(
					'font-normal hover:font-medium normal-case')
			with mini_card('space-x-2'):
				ui.button(text='How to Subscribe', icon='lightbulb',
						  # TODO Add the How to to aktivismus.org
						  on_click=lambda: ui.navigate.to(
							  'https://pad.kanthaus.online/Nextcloud?both=#Subscribe-to-Calendars',
							  new_tab=True)
						  ).props('flat color=white').classes(
					'font-normal hover:font-medium normal-case')

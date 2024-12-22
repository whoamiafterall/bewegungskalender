from nicegui import ui
from slugify import slugify
from sqlmodel import select

from bewegungskalender.backend.calendar.category import Category
from bewegungskalender.backend.io import db
from bewegungskalender.frontend.filter.controllers.category_filter_controller import CATEGORY_FILTER
from bewegungskalender.frontend.filter.filter import call_refresh_filter_event
from bewegungskalender.frontend.functions import mini_card, opacity

async def category_filters_ui():
	await ui.context.client.connected()
	categories = db.exe(select(Category)).all()
	
	# Heading
	#	with ui.row().classes('flex align-center'):
	#		ui.label('Kategorien').classes('text-base font-medium')

	# Create Buttons with useful Information and Links for each Category
	for category in categories:
		with mini_card('w-full py-0 px-0 m-0'):
			# Check Box
			with ui.checkbox(value=True).classes('px-0').on_value_change(call_refresh_filter_event).bind_value(CATEGORY_FILTER.categories[f"{slugify(str(category.internal))}"]):
				ui.tooltip(category.description).classes(
					'text-balance text-sm font-medium text-center sm:w-[300px]').style(
					f"background-color:{category.color}").props('delay=150 hide-delay=200')

			# Dropdown Button
			with ui.dropdown_button(
					text=category.name,
					color=opacity(70, category.color),
					auto_close=True,
			).classes('font-normal text-sm capitalize hover:font-medium grow items-start'):
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
					
		
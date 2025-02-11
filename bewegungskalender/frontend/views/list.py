from datetime import datetime, timedelta

import requests
from nicegui import ui
from slugify import slugify

from bewegungskalender.backend.calendar.event import Event
from bewegungskalender.backend.calendar.location import LocationType
from bewegungskalender.backend.formatting.format import event_time
from bewegungskalender.backend.io.config import MENU
from bewegungskalender.backend.io.credentials import NC_DOMAIN
from bewegungskalender.frontend.filter.filter import events_using_filters
from bewegungskalender.frontend.filter.filters.category_filter import categories_filters_ui, CATEGORY_FILTER
from bewegungskalender.frontend.filter.filters.duration_filter import duration_filter_ui, DURATION_FILTER
from bewegungskalender.frontend.filter.filters.location_proximity_filter import location_proximity_filter_ui, \
	LOCATION_PROXIMITY_FILTER
from bewegungskalender.frontend.filter.filters.location_type_filter import LOCATION_TYPE_FILTER, location_type_filter_ui
from bewegungskalender.frontend.filter.filters.time_filter import MONTH_FILTER, month_filter_ui
from bewegungskalender.frontend.helpers.functions import loading, container, icon_link, opacity
from bewegungskalender.frontend.helpers.functions import mini_card
from bewegungskalender.frontend.navigation.router import ROUTER


# Create List Page
@ROUTER.add('/')
async def list_view():
	await ui.context.client.connected()
	loading(MENU['list']['label'])
	
	with container('h-[calc(100vh-55px)] pb-0 mb-50px justify-between flex-row'):

		with ui.column(wrap=False, align_items='center').classes(
				'h-full w-full m-0 gap-0 gap-y-1 md:px-2 overflow-x-auto'):
			with ui.row(align_items='center').classes('gap-0 w-full'):
				with ui.element().classes('sm:hidden mx-auto my-2'):
					month_filter_ui()
				with ui.element().classes('row flex-row mx-auto flex-nowrap h-10 float-right overflow-x-auto'):
					location_type_filter_ui()
			await create_list_ui()
		
		# Filter
		with ui.column(wrap=False, align_items='start').classes(
				'gap-1 h-full w-66 px-3 text-sm max-md:hidden'):
			duration_filter_ui()
		#	location_type_filter_ui()
			location_proximity_filter_ui()
			await categories_filters_ui()
		
		ui.on('refresh_filter', lambda: create_list_ui.refresh(), throttle=1)


# -----------------
# Show Events applying current filters

@ui.refreshable
async def create_list_ui():
	# Get filtered Events
	events = events_using_filters(
		[LOCATION_TYPE_FILTER, MONTH_FILTER, CATEGORY_FILTER, LOCATION_PROXIMITY_FILTER, DURATION_FILTER])

	with ui.list().classes('w-full scroll'):
		for event in events:
			today = datetime.today().date()
			if event.start.date() <= today <= event.start.date() + event.duration:
				today_label(today)
				event_row(event).classes('border-current sm:border sm:rounded')
			elif event.start.date() - timedelta(days=1) == today or event.end.date() + timedelta(days=1) == today:
				today_label(today)
				event_row(event)
			else:
				event_row(event)


def event_row(event: Event, classes: str = None) -> ui.row:
	# Create a row for each event
	with (ui.row().classes('flex flex-row w-full gap-0 p-0.5 items-center text-sm') as row):
		# Create the expansion item
		caption = f"{event_time(event.start, event.end, '%d.%m.')} {event.location.name}"
		with ui.expansion(event.summary, caption=caption, icon=event.location.type.icon, group='events'
		                  ).props(
			'hide-expand-icon dense switch-toggle-side label-lines=1 caption-lines=1 header-class=font-normal'
		).style(f"background-color:{opacity(event.category.color)}"
		        ).classes('grow max-w-full rounded'):
			# Create the dropdown content
			with mini_card('flex-col p-2 gap-y-1 text-sm w-full'):
				with ui.row().classes():
					icon_link('event', event_time(event.start, event.end, '%A, %d.%m.'))
					match event.location.type:
						case LocationType.local:
							icon_link(event.location.type.icon, event.location.name, event.location.osm_link)
						case _:
							icon_link(event.location.type.icon, event.location.type.keyword)
				if event.link:
					icon_link('link', event.link.removeprefix('https://'), event.link)
				if event.description is not None and event.description.strip() != event.link:
					ui.label(event.description).classes('text-pretty px-3 shrink mx-auto')
				download_button(event)
		#  show_location(event)  # Show Event_Location
		row.classes(classes)
	return row


# -----------------
# Helper Functions
def today_label(today):
	ui.markdown(f"Heute: {today:%A, %x}").classes('mx-auto font-medium text-sm w-full text-center')


def show_time(event: Event):
	with mini_card('sm:p-1 gap-1 order-last'):
		ui.label(event_time(event.start, event.end, '%d (%a)')).classes('mr-auto')
	ui.space().classes('grow sm:hidden')


def show_location(event: Event):
	with mini_card('max-sm:order-2 sm:align-right order-last'):
		match event.location.type:
			case LocationType.online | LocationType.international | LocationType.national:
				icon_link(event.location.type.icon, card_classes='py-0 px-0')
			case LocationType.local:
				text = event.location.city if event.location.city is not None else event.location.name
				ui.label(text).classes('grow text-right')


def download_ics(url, name):
	ui.download(requests.get(url).text, name)


def download_button(event: Event):
	""" Create download button for the event
	In order to download we first fetch the ics contents and then serve them to the client.
	We need to do it this way because else nice gui passes some headers that mess with next cloud authentication
	"""
	print(f"https://{NC_DOMAIN}/remote.php/dav/public-calendars/{event.category.public_id}/{event.cloud_id}.ics?export")
	ui.button(text='Add to Calendar (.ics)', icon='file_download',
	          on_click=lambda: download_ics(
		          f"https://{NC_DOMAIN}/remote.php/dav/public-calendars/{event.category.public_id}/{event.ics_url.split('/')[-1]}?export",
		          f"{slugify(event.summary)}.ics")
	          ).props('flat'
	                  ).classes('font-normal normal-case text-secondary bg-primary')
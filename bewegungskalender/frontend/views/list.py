from datetime import datetime

import requests
from nicegui import ui
from slugify import slugify

from bewegungskalender.backend.calendar.event import Event
from bewegungskalender.backend.calendar.location import EventLocationType
from bewegungskalender.backend.formatting.format import event_time
from bewegungskalender.backend.io.config import MENU
from bewegungskalender.backend.io.credentials import NC_DOMAIN
from bewegungskalender.frontend.filter.filter import events_using_filters
from bewegungskalender.frontend.filter.filters.category_filter import categories_filters_ui, CATEGORY_FILTER
from bewegungskalender.frontend.filter.filters.duration_filter import duration_filter_ui, DURATION_FILTER
from bewegungskalender.frontend.filter.filters.location_proximitry_filter import location_proximity_filter_ui, \
    LOCATION_PROXIMITY_FILTER
from bewegungskalender.frontend.filter.filters.location_type_filter import location_type_filter_ui, LOCATION_TYPE_FILTER
from bewegungskalender.frontend.filter.filters.time_filter import month_filter_ui, TIME_FILTER
from bewegungskalender.frontend.helpers.functions import loading, container, dropdown_button, icon_link
from bewegungskalender.frontend.helpers.functions import mini_card
from bewegungskalender.frontend.navigation.router import ROUTER


# Create List Page
@ROUTER.add('/')
async def list_view():
    loading(MENU['list']['label'])
    await ui.context.client.connected()
    
    with container('h-[calc(100vh-55px)] pb-0 mb-50px justify-between flex-row'):

        await create_list_ui()
        
        # Filter
        with ui.column(wrap=False, align_items='start').classes(
                'gap-1 w-1/4 h-full fixed right-5 px-3 text-sm max-lg:hidden'):
            duration_filter_ui()
            location_type_filter_ui()
            location_proximity_filter_ui(
                                ).bind_visibility_from(LOCATION_TYPE_FILTER.state, target_name="value",
                                backward=lambda v: (EventLocationType.local
                                                    or EventLocationType.national
                                                    or EventLocationType.international in v))
            await categories_filters_ui()
    
        ui.on('refresh_filter', lambda: create_list_ui.refresh(), throttle=0.1, leading_events=False)

# -----------------
# Show Events applying current filters

@ui.refreshable
async def create_list_ui():
    # Get filtered Events
    events = events_using_filters([LOCATION_TYPE_FILTER, TIME_FILTER, CATEGORY_FILTER, LOCATION_PROXIMITY_FILTER, DURATION_FILTER])
    with ui.column(wrap=False, align_items='center').classes('h-full w-full lg:w-3/4 m-0 gap-0 gap-y-1 sm:px-2'):
        month_filter_ui()
   #     ui.notify("Wische nach links oder rechts um den vorherigen oder nächsten Monat anzuzeigen!", position="top")
   #     with ui.carousel(animated=True).classes('h-full w-full bg-primary').props('swipeable infinite') as carousel:
           # for month in TIME_FILTER.month.value:
            #    with ui.carousel_slide(name=month):
        with ui.list().classes('w-full max-sm:divide-y divide-current'):
            for event in events:
                create_event_row(event)

def create_event_row(event):
    # Create a row for each event
    with ui.row().classes('flex flex-row w-full gap-0 sm:gap-x-3 p-0.5 max-sm:mb-2 items-center text-sm') as event_row:
        if event.start.date() == datetime.today().date():
            event_row.classes('border-current sm:border sm:rounded')
        show_time(event)  # Show Event_Time
        # Create the dropdown button
        with dropdown_button(event.summary, event.category.color, "max-sm:w-full max-sm:order-3"):
            # Create the dropdown content
            with mini_card('flex-col p-2 gap-y-1 text-sm w-full'):
                with ui.row().classes():
                    icon_link('event', event_time(event.start, event.end))
                    if event.location.type == EventLocationType.online:
                        icon_link('computer', "Online")
                    if event.location.type == EventLocationType.local:
                        icon_link('map', event.location.name, event.location.osm_link)
                if event.link:
                    icon_link('link', event.link.removeprefix('https://'), event.link)
                if event.description.strip() != event.link:
                    ui.label(event.description).classes('text-pretty px-3 shrink mx-auto')
                download_button(event)
        show_location(event)  # Show Event_Location

# -----------------
# Helper Functions

def show_time(event:Event):
    with mini_card('sm:p-1 gap-1 order-first'):
        ui.label(f"{event.start:%d (%a)}")
        ui.label(f"{event.start:%H:%M}:") if event.start.time() != datetime.min.time() else None
        ui.label(f"{event.end:- %d (%a):}") if event.start.date() != event.end.date() else None
    ui.space().classes('grow sm:hidden')
    
def show_location(event:Event):
    with mini_card('max-sm:order-2 sm:align-right order-last'):
        match event.location.type:
            case EventLocationType.online | EventLocationType.international | EventLocationType.national:
                ui.label(f"{event.location.name}").classes('grow text-right')
            case EventLocationType.undefined:
                ui.space()
            case EventLocationType.local:
                if event.location.country_code in ('de', 'at', 'ch'):
                    text = event.location.city if event.location.city is not None else event.location.name
                    ui.label(f"{text}").classes('grow text-right')
                elif not event.location.country_code:
                    ui.space()
                else:
                    ui.label(f"{event.location.country}").classes('grow text-right')
   
def download_ics(url, name):
        ui.download(str.encode(requests.get(url).text), name)

def download_button(event:Event):
    """ Create download button for the event
    In order to download we first fetch the ics contents and then serve them to the client.
    We need to do it this way because else nice gui passes some headers that mess with next cloud authentication
    """
    ui.button(text='Add to Calendar (.ics)', icon='file_download',
              on_click=lambda: download_ics(
              f"https://{NC_DOMAIN}/remote.php/dav/public-calendars/{event.category.public_id}/{event.cloud_id}.ics?export",
              f"{slugify(event.summary)}.ics")
          ).props('flat'
    ).classes('font-normal normal-case text-secondary bg-primary')
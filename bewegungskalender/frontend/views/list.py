from contextlib import contextmanager
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
from bewegungskalender.frontend.helpers.functions import loading, container, dropdown_button, icon_link
from bewegungskalender.frontend.helpers.functions import mini_card
from bewegungskalender.frontend.navigation.router import ROUTER


# Create List Page
@ROUTER.add('/')
async def list_view():
    await ui.context.client.connected()
    loading(MENU['list']['label'])
    
    with container('h-[calc(100vh-55px)] pb-0 mb-50px justify-between flex-row'):

        await create_list_ui()
        
        # Filter
        with ui.column(wrap=False, align_items='start').classes(
                'gap-1 w-1/4 h-full fixed right-5 px-3 text-sm max-lg:hidden'):
            duration_filter_ui()
            location_type_filter_ui()
            location_proximity_filter_ui(
                                ).bind_visibility_from(LOCATION_TYPE_FILTER.state, target_name="value",
                                                       backward=lambda v: (LocationType.local
                                                                           or LocationType.national
                                                                           or LocationType.international in v))
            await categories_filters_ui()
    
        ui.on('refresh_filter', lambda: create_list_ui.refresh(), throttle=1)

# -----------------
# Show Events applying current filters

@ui.refreshable
async def create_list_ui():
    # Get filtered Events
    events = events_using_filters([LOCATION_TYPE_FILTER, MONTH_FILTER, CATEGORY_FILTER, LOCATION_PROXIMITY_FILTER, DURATION_FILTER])
    with ui.column(wrap=False, align_items='center').classes('h-full w-full lg:w-3/4 m-0 gap-0 gap-y-1 sm:px-2'):
        with ui.row(align_items='start').classes('gap-0 w-full'):
            month_filter_ui()
            ui.space()
            with ui.element().classes('row flex-row flex-nowrap h-10 float-right overflow-x-auto no-scrollbar'):
               location_types()
        
        #     ui.notify("Wische nach links oder rechts um den vorherigen oder nächsten Monat anzuzeigen!", position="top")
   #     with ui.carousel(animated=True).classes('h-full w-full bg-primary').props('swipeable infinite') as carousel:
           # for month in MONTH_FILTER.month.value:
            #    with ui.carousel_slide(name=month):
        with ui.list().classes('w-full max-sm:divide-y divide-current scroll'):
            for event in events:
                today = datetime.today().date()
                if event.start.date() <= today <= event.start.date() + event.duration:
                    today_label(today)
                    event_row(event, classes='border-current sm:border sm:rounded')
                elif event.start.date() - timedelta(days=1) == today:
                    today_label(today)
                elif event.end.date() + timedelta(days=1) == today:
                    today_label(today)
                else:
                    event_row(event)

@contextmanager
def event_row(event:Event, classes:str=None) -> ui.row:
    # Create a row for each event
    with ui.row().classes('flex flex-row w-full gap-0 sm:gap-x-3 p-0.5 max-sm:mb-2 items-center text-sm') as row:
        show_time(event)  # Show Event_Time
        # Create the dropdown button
        with dropdown_button(event.summary, event.category.color, "max-sm:w-full max-sm:order-3"):
            # Create the dropdown content
            with mini_card('flex-col p-2 gap-y-1 text-sm w-full'):
                with ui.row().classes():
                    icon_link('event', event_time(event.start, event.end, '%A, %d.%m.'))
                    match event.location.type:
                        case LocationType.local:
                            icon_link(event.location.type.icon, event.location.name, event.location.osm_link)
                        case _:
                            icon_link(event.location.type.icon, event.location.name)
                if event.link:
                    icon_link('link', event.link.removeprefix('https://'), event.link)
                if event.description is not None and event.description.strip() != event.link:
                    ui.label(event.description).classes('text-pretty px-3 shrink mx-auto')
                download_button(event)
        show_location(event)  # Show Event_Location
        row.classes(classes)
    return row

# -----------------
# Helper Functions

def location_types():
    chip(LocationType.local)
    chip(LocationType.national)
    chip(LocationType.international)
    chip(LocationType.online)

def chip(location_type:LocationType):
    ui.chip(text=location_type.keyword, icon=location_type.icon, color='secondary', selectable=True).props('outline icon-selected=highlight_off')

def today_label(today):
    ui.markdown(f"Heute: {today:%A, %x}").classes('mx-auto font-medium text-sm w-full text-center')

def show_time(event:Event):
    with mini_card('sm:p-1 gap-1 order-first'):
        ui.label(event_time(event.start, event.end, '%d (%a)')).classes('mr-auto')
    ui.space().classes('grow sm:hidden')
    
def show_location(event:Event):
    with mini_card('max-sm:order-2 sm:align-right order-last'):
        match event.location.type:
            case LocationType.online | LocationType.international | LocationType.national:
                icon_link(event.location.type.icon, card_classes='py-0 px-0')
            case LocationType.local:
                text = event.location.city if event.location.city is not None else event.location.name
                ui.label(text).classes('grow text-right')
               
   
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
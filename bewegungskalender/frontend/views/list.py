from datetime import datetime

import requests
from nicegui import ui
from slugify import slugify
from sqlalchemy import false

from bewegungskalender.backend.calendar.event import Event
from bewegungskalender.backend.calendar.location import LocationType
from bewegungskalender.backend.formatting.format import event_time
from bewegungskalender.backend.io.config import MENU
from bewegungskalender.backend.io.credentials import NC_DOMAIN
from bewegungskalender.frontend.filter.filter import events_using_filters
from bewegungskalender.frontend.filter.filters.category_filter import categories_filters_ui, CATEGORY_FILTER
from bewegungskalender.frontend.filter.filters.duration_filter import duration_filter_ui, DURATION_FILTER
from bewegungskalender.frontend.filter.filters.location_type_filter import LOCATION_TYPE_FILTER, location_type_filter_ui
from bewegungskalender.frontend.filter.filters.recurring_filter import RECURRING_FILTER, recurring_filter_ui
from bewegungskalender.frontend.filter.filters.time_filter import MONTH_FILTER, month_filter_ui
from bewegungskalender.frontend.helpers.functions import loading, container, icon_link, opacity
from bewegungskalender.frontend.helpers.functions import mini_card
from bewegungskalender.frontend.navigation.router import ROUTER


# Create List Page
@ROUTER.add('/')
async def list_view():
    await ui.context.client.connected()
    loading(MENU['list']['label'])
    
    # Main Container
    with container('pb-1 max-sm:pt-2 justify-between flex-row'):
        # Left (Main) Column for Events and the Filters above
        with ui.element().classes(
                'h-full flex items-center w-full m-0 gap-0 gap-y-1 md:px-2 overflow-x-auto'):
            with ui.row(align_items='center').classes('gap-0 w-full'):
                with ui.element().classes('md:hidden mx-auto my-2'):
                    month_filter_ui()
                with ui.element().classes('row flex-row mx-auto flex-nowrap h-10 float-right overflow-x-auto'):
                        location_type_filter_ui()
            await create_list_ui()
        
        # Right Column for the Filters that disappear into drawer
        with ui.column(wrap=False, align_items='start').classes(
                'gap-1 h-full w-66 px-3 text-sm max-md:hidden'):
            with mini_card('w-full p-0'):
                duration_filter_ui()
                recurring_filter_ui()
            await categories_filters_ui()
        ui.on('refresh_filter', lambda: create_list_ui.refresh(), throttle=1)


# -----------------
# Show Events applying current filters

@ui.refreshable
async def create_list_ui():
    # Get filtered Events
    filters = [LOCATION_TYPE_FILTER, MONTH_FILTER, RECURRING_FILTER, CATEGORY_FILTER, DURATION_FILTER]
    events = events_using_filters(filters,True) # Set to true for testing TODO: Merge r events with normal events
    # r_events = events_using_filters(filters,True)

    with ui.list().classes('lg:w-4/5 w-full mx-auto scroll'):
        today = datetime.today().date()
        prev_event = None; checked = False
        for count, event in enumerate(events):
            prev_start = today if not prev_event else prev_event.start.date()
            if MONTH_FILTER.month.value == today.month:
                # If today is between the previous event's start and this event's start or during this event insert today_label()
                if event.start.date() + event.duration >= today >= event.start.date() or event.start.date() >= today >= prev_start:
                    if not checked:
                        today_label(today)
                        checked = True
                    event_row(event)
                elif count == len(events)-1:
                    if not checked:
                        today_label(today)
                        checked = True
                    event_row(event)
                else:
                    event_row(event)
            else:
                event_row(event)
            prev_event = event


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
                        case LocationType.undefined:
                            icon_link(event.location.type.icon, event.location.name)
                        case _:
                            icon_link(event.location.type.icon, event.location.type.keyword)
                if event.link:
                    icon_link('link', event.link.removeprefix('https://'), event.link)
                if event.description is not None and event.description.strip() != event.link:
                    ui.label(event.description).classes('text-pretty px-3 shrink mx-auto')
                download_button(event)
        row.classes(classes)
    return row


# -----------------
# Helper Functions
def today_label(today):
    ui.markdown(f"Heute: {today:%A, %x}").classes('mx-auto font-medium text-sm w-full border-current border rounded text-center').mark('today')

def download_ics(url, name):
    ui.download(requests.get(url).text, name)


def download_button(event: Event):
    """ Create download button for the event
    In order to download we first fetch the ics contents and then serve them to the client.
    We need to do it this way because else nice gui passes some headers that mess with next cloud authentication
    """
    ui.button(text='Add to Calendar (.ics)', icon='file_download',
              on_click=lambda: download_ics(
                  f"https://{NC_DOMAIN}/remote.php/dav/public-calendars/{event.category.public_id}/{event.ics_url.split('/')[-1]}?export",
                  f"{slugify(event.summary)}.ics")
              ).props('flat'
                      ).classes('font-normal normal-case text-secondary bg-primary')
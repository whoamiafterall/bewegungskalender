from datetime import datetime

import requests
from dateutil.utils import today
from nicegui import ui
from slugify import slugify

from bewegungskalender.backend.calendar.event import Event
from bewegungskalender.backend.calendar.location import EventLocationType
from bewegungskalender.backend.io.config import MENU
from bewegungskalender.backend.io.credentials import NC_DOMAIN
from bewegungskalender.frontend.filter.filter_controller import FILTER
from bewegungskalender.frontend.filter.ui.category_filter import category_filters
from bewegungskalender.frontend.filter.ui.location_filter import location_filter
from bewegungskalender.frontend.filter.ui.online_filter import online_filter
from bewegungskalender.frontend.filter.ui.time_filter import duration_filter
from bewegungskalender.frontend.functions import loading, container, icon_link, dropdown_button
from bewegungskalender.frontend.functions import mini_card
from bewegungskalender.frontend.navigation.router import ROUTER


# Create List Page
@ROUTER.add('/', True)
async def list_view():
    loading(MENU['list']['label'])
    await ui.context.client.connected()
    
    with container('xl:w-4/5 w-full justify-between flex-row'):
        # Populate Event List using filter
        @ui.refreshable
        async def create_list_ui():
            
            # Get filtered Events
            events = FILTER.events_using_filter()
            
            # Clear list view before filter was applied
            with ui.column(wrap=False, align_items='center').classes('grow m-0 gap-0 px-2'):
                
                with ui.list().classes('w-full'):
                    month = today().month
                    for event in events:
                        if event.start.month != month:
                            month_heading(event.start)
                        month = event.start.month
                        
                        # Create a row for each event
                        with ui.row().classes('flex flex-row w-full gap-1 p-0.5 max-sm:mb-2 text-sm'):
                            show_time(event)
                            
                            # Create the summary dropdown button
                            with dropdown_button(event.summary, event.category.color, "max-sm:w-full max-sm:order-3"):
                                # Create the dropdown content
                                with mini_card('flex-col text-sm w-full'):
                                    if event.location.type == EventLocationType.online:
                                        icon_link('Computer', event.location.name, event.location.online_link)
                                    if event.location.type == EventLocationType.offline:
                                        icon_link('map', event.location.name, event.location.osm_link)
                                    if event.link:
                                        icon_link('link', event.link, event.link)
                                    download(event)
                            show_location(event)
        
        await create_list_ui()
        
        # Filter
        with ui.column(wrap=False, align_items='start').classes(
                'm-0 gap-1 max-w-1/4 pt-5 px-3 shrink text-sm max-lg:hidden'):
            duration_filter()
            online_filter()
            location_filter()
            await category_filters()
        
        ui.on('refresh_filter', lambda: create_list_ui.refresh(), throttle=0.1, leading_events=False)
  
  
# -----------------
# Helper Functions

def month_heading(month:datetime=today()):
    with ui.row().classes('justify-center'):
        ui.markdown(f"#### {month:%B}").classes('text-center')
        
def show_time(event:Event):
    with mini_card('p-1 gap-1 order-first'):
        ui.label(f"{event.start:%d (%a)}").classes('nowrap')
        ui.label(f"{event.start:%H:%M}:") if event.start.time() != datetime.min.time() else None
    ui.space().classes('grow sm:hidden')
    
def show_location(event:Event):
    with mini_card('max-sm:order-2 sm:align-right order-last'):
        match event.location.type:
            case EventLocationType.online:
                ui.label(f"Online").classes('grow text-right')
            case EventLocationType.undefined:
                ui.space()
            case EventLocationType.offline:
                if event.location.country_code in ('de', 'at', 'ch'):
                    ui.label(f"{event.location.city}").classes('grow text-right')
                elif not event.location.country_code:
                    ui.space()
                else:
                    ui.label(f"{event.location.country}").classes('grow text-right')
   
def download_ics(url, name):
        ui.download(str.encode(requests.get(url).text), name)

def download(event:Event):
    """ Create download button for the event
    In order to download we first fetch the ics contents and then serve them to the client.
    We need to do it this way because else nice gui passes some headers that mess with next cloud authentication
    """
    ui.button(text='Add to Calendar (.ics)', icon='file_download',
              on_click=lambda: download_ics(
              f"https://{NC_DOMAIN}/remote.php/dav/public-calendars/{event.category.public_id}/{event.ics_url.split('/')[-1]}?export",
              f"{slugify(event.summary)}.ics")
          ).props('flat color=white'
    ).classes('font-normal hover:font-medium normal-case')


from datetime import datetime

import requests
from dateutil.utils import today
from nicegui import ui,observables,binding
from slugify import slugify

from bewegungskalender.backend.io.config import MENU
from bewegungskalender.backend.io.credentials import NC_DOMAIN
from bewegungskalender.frontend.filter.ui.category_filter import category_filters
from bewegungskalender.frontend.filter.filter_controller import FILTER, call_refresh_filter_event
from bewegungskalender.frontend.filter.ui.location_filter import location_filter
from bewegungskalender.frontend.filter.ui.time_filter import duration_filter
from bewegungskalender.frontend.functions import loading, container, opacity
from bewegungskalender.frontend.functions import mini_card
from bewegungskalender.frontend.navigation.router import ROUTER


def heading(month:datetime=today()):
    with ui.row().classes('justify-center'):
        ui.markdown(f"#### {month:%B}").classes('text-center')

# Create List Page
@ROUTER.add('/',True)
async def list_view():
    loading(MENU['list']['label'])
    await ui.context.client.connected()
    
    # Create Buttons linking to Nextcloud views
  #  with ui.row().classes('m-0  gap-0 text-sm sm:text-base max-sm:hidden'):
   #     view_buttons('max-sm:hidden')
    
    with container('xl:w-4/5 w-full justify-between flex-row'):


        def download_ics(url, name):
            ui.download(str.encode(requests.get(url).text), name)


        # Populate Event List using filter
        @ui.refreshable
        def create_list_ui():
            
            # Get filtered Events
            events = FILTER.events_using_filter()

            # Clear list view before filter was applied
            with ui.column(wrap=False, align_items='center').classes('grow m-0 gap-0 px-2'):

                with ui.list().classes('w-full'):
                    month = today().month
                    for event in events:
                        if event.start.month != month:
                            heading(event.start)
                        month = event.start.month

                        # Create a row for each event
                        with ui.row().classes('flex flex-row w-full gap-1 p-0.5 max-sm:mb-2 text-sm') as event_item:

                            # Create the time
                            with mini_card('p-1 gap-1 order-first'):
                                ui.label(f"{event.start:%d (%a)}").classes('nowrap')
                                ui.label(f"{event.start:%H:%M}:") if event.start.time() != datetime.min.time() else None
                            ui.space().classes('grow sm:hidden')

                            # Create the city/country
                            with mini_card('max-sm:order-2 sm:align-right order-last'):
                                if event.location.country_code in ('de','at','ch'):
                                    ui.label(f"{event.location.city}").classes('grow text-right')
                                elif not event.location.country_code:
                                    ui.space()
                                else:
                                    ui.label(f"{event.location.country}").classes('grow text-right')

                            # Create the summary dropdown button
                            with ui.dropdown_button(
                                    text=event.summary,
                                    color=opacity(60, event.category.color),
                                    auto_close=True
                            ).classes('font-normal text-sm capitalize hover:font-medium max-sm:w-full max-sm:order-3 grow items-start'):


                                # Create the dropdown content
                                with mini_card('flex-col text-sm w-full'):
                                    if event.location.name != "nicht bekannt":
                                        with mini_card('space-x-2'):
                                            ui.icon('link', size='20px')
                                            ui.link(event.location.name, event.location.osm_link, new_tab=True)
                                    if event.link:
                                        with mini_card('space-x-2'):
                                            ui.icon('map', size='20px')
                                            ui.link(event.link, event.link, new_tab=True)


                                    # Create donwload button
                                    # In order to download we first fetch the isc contents and then serve them to the client.
                                    # We need to to it this way because else nice gui passes some headers that mess with next cloud authentication

                                    # TODO: event.ics_url is useless as it requires authentication. We should perhaps just catch the id we split out of ics_url here instead

                                    ui.button(text='Add to Calendar (.ics)', icon='file_download',
                                              on_click=lambda: download_ics(
                                                  f"https://{NC_DOMAIN}/remote.php/dav/public-calendars/{event.category.public_id}/{event.ics_url.split('/')[-1]}?export",
                                                  f"{slugify(event.summary)}.ics")
                                              ).props('flat color=white').classes(
                                        'font-normal hover:font-medium normal-case')

        create_list_ui()


        # Filter
        with ui.column(wrap=False, align_items='start').classes(
                'm-0 gap-1 max-w-1/4 pt-5 px-3 shrink text-sm max-lg:hidden'):
            duration_filter()
            location_filter()

            await category_filters()


        ui.on('refresh_filter', lambda: create_list_ui.refresh(),throttle=0.1,trailing_events=False)

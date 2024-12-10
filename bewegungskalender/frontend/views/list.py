from datetime import datetime

from dateutil.utils import today
from nicegui import ui
from slugify import slugify

from bewegungskalender.backend.io.config import MENU
from bewegungskalender.backend.io.credentials import NC_DOMAIN
from bewegungskalender.frontend.filter import Eventfilter
from bewegungskalender.frontend.functions import loading, container, opacity
from bewegungskalender.frontend.functions import mini_card
from bewegungskalender.frontend.navigation.router import ROUTER


def heading(month:datetime=today()):
    return ui.markdown(f"#### {month:%B}").classes('text-center')

# Create List Page
@ROUTER.add(f"/{slugify(str(MENU['list']['label'].lower()))}")
async def list_view():
    loading(MENU['list']['label'])
    await ui.context.client.connected()

    with (container('xl:w-1/2 lg:w-3/5 md:w-4/5 max-sm:w-full')):
        #        ui.label('Einige kürzere Termine werden nicht angezeigt. Bearbeite die Filter einstellungen um dies zu ändern.')
        
        #
        ui_list_element = ui.list().classes('w-full')
        events_ui_list = []
        def use_filter():
            
            # Get filtered Events
            events = filterUI.events_using_filter()
            
            # Clear list view before filter was applied
            with ui_list_element:
                for event_ui in events_ui_list:
                    event_ui.delete()
                events_ui_list.clear()
                
                # Create headings
                events_ui_list.append(heading())
                month = today().month
                for event in events:
                    if event.start.month != month:
                        events_ui_list.append(heading(event.start))
                    month = event.start.month
                    
                    # Create a row for each event
                    with ui.row().classes('flex flex-row gap-0 max-sm:mb-2 text-sm sm:text-base') as event_item:
                        
                        # Create the time
                        with mini_card('p-1 order-first'):
                            ui.label(f"{event.start:%d (%a)}").classes('w-[60px]')
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
                        ).classes('font-normal text-sm sm:text-base capitalize hover:font-medium max-sm:w-full max-sm:order-3 grow items-start'):
                            
                            
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
                                          on_click=lambda: ui.download(str.encode(f"https://{NC_DOMAIN}/remote.php/dav/public-calendars/{event.category.public_id}/{event.ics_url.split('/')[-1]}?export"),
                                          f"{slugify(event.summary)}.isc")
                                          ).props('flat color=white').classes('font-normal hover:font-medium normal-case')
                                
                      
                    

                    events_ui_list.append(event_item)
        
        
        filterUI = Eventfilter(use_filter)
        use_filter()
    
        

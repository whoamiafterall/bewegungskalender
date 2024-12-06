from datetime import datetime

from dateutil.utils import today
from nicegui import ui, html
from slugify import slugify

from bewegungskalender.backend.formatting.format import event_time
from bewegungskalender.backend.io.config import MENU, CALDAV_URL, CALDAV_USR, CALDAV_PW
from bewegungskalender.frontend.filter import Eventfilter
from bewegungskalender.frontend.functions import loading, container, opacity
from bewegungskalender.frontend.navigation.router import ROUTER

# Create List Page
@ROUTER.add(f"/{slugify(str(MENU['list']['label'].lower()))}")
async def list_view():
    loading(MENU['list']['label'])
    await ui.context.client.connected()

    with (container('xl:w-1/2 lg:w-3/5 md:w-4/5 max-sm:w-full')):
        #        ui.label('Einige kürzere Termine werden nicht angezeigt. Bearbeite die Filter einstellungen um dies zu ändern.')
        
        ui_list_element = ui.list().classes('w-full')
        events_ui_list = []
        def use_filter():
            events = filterUI.events_using_filter()
            
            with ui_list_element:
                for event_ui in events_ui_list:
                    event_ui.delete()
                events_ui_list.clear()
                events_ui_list.append(ui.markdown(f"#### {today():%B}").classes('text-center'))
                month = today().month
                for event in events:
                    if event.start.month != month:
                        events_ui_list.append(ui.markdown(f"#### {event.start:%B}").classes('text-center'))
                    month = event.start.month
                    
                    # The row for each event
                    with ui.row().classes('flex break-words flex-row gap-0 max-sm:mb-2') as event_item:
                        with ui.card().tight().classes('m-0 p-1 sm:p-2 flex-row bg-black float-left order-first'):
                            ui.label(f"{event.start:%d (%a)}").classes('w-[60px]')
                            ui.label(f"{event.start:%H:%M}:") if event.start.time() != datetime.min.time() else None
                        ui.space().classes('grow sm:hidden')
                        with ui.card().tight().classes('m-0 p-1 sm:p-2 flex-row bg-black max-sm:order-2 sm:align-right order-last'):
                            if event.location.country_code in ('de','at','ch'):
                                ui.label(f"{event.location.city}").classes('grow text-right')
                            elif not event.location.country_code:
                                ui.space()
                            else:
                                ui.label(f"{event.location.country}").classes('grow text-right')
                        
                        with ui.dropdown_button(
                                text=event.summary,
                                color=opacity(60, event.category.color),
                                auto_close=True
                        ).classes('font-normal capitalize hover:font-medium max-sm:w-full max-sm:order-3 grow items-start'):
                            
                            # DropDown Content
                            with ui.card().tight(
                            ).classes('m-0 p-2 flex-row space-x-3 items-center bg-primary text-white font-medium float-left'):
                                if event.location.name != "nicht bekannt":
                                    ui.link(f"📌: {event.location.name}", event.location.osm_link, new_tab=True)
                                if event.link:
                                    ui.link(f"🔎: {event.link}", event.link, new_tab=True)
                                ui.button(icon='file_download',
                                          on_click=lambda: ui.download(event.ics_url)
                                          ).props('flat color=white')
                            
                            #TODO find out how to solve authentication problem
                            #  print(event.ics_url)
                            # print(f"{CALDAV_URL}public-calendars/{event.category.public_id}/{event.cloud_id}.ics?export")
                            #print(f"{CALDAV_URL}public-calendars/{event.category.public_id}/{event.ics_url.split('/')[-1]}?export")
                    
                    events_ui_list.append(event_item)
        
        
        filterUI = Eventfilter(use_filter)
        use_filter()
    
        

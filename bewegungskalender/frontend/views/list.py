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
def list_view():
    loading(MENU['list']['label'])

    with container('xl:w-1/2 max-xl:w-full'):
#        ui.label('Einige kürzere Termine werden nicht angezeigt. Bearbeite die Filter einstellungen um dies zu ändern.')

        def use_filter():
            events = filterUI.events_using_filter()

            with ui.list().classes('w-full'):
                events_ui_list = []
                for event_ui in events_ui_list:
                    event_ui.delete()
                events_ui_list.clear()
                ui.markdown(f"#### {today():%B}").classes('text-center'); month = today().month
                for event in events:
                    if event.start.month != month:
                        ui.markdown(f"#### {event.start:%B}").classes('text-center')
                    month = event.start.month
                    with ui.row().classes('flex flex-row') as event_item:
                        with ui.card().tight().classes('m-0 p-2 flex-row bg-black float-left'):
                            ui.label(f"{event.start:%d (%a)}").classes('w-[60px]')
                            ui.label(f"{event.start:%H:%M}:") if event.start.time() != datetime.min.time() else None
                        with ui.dropdown_button(
                                text=event.summary,
                                color=opacity(70, event.category.color),
                                auto_close=True).classes('font-normal capitalize hover:font-medium text-break grow items-start'):
                            with ui.card().tight().classes('m-0 p-2 flex-row space-x-3 items-center bg-primary text-white font-medium float-left'):
                                if event.location.name != "nicht bekannt":
                                    ui.link(f"📌: {event.location.name}", event.location.osm_link, new_tab=True)
                                if event.link:
                                    ui.link(f"🌐: {event.link}", event.link, new_tab=True)
                                ui.button(icon='file_download',
                                          on_click=lambda: ui.download(event.ics_url)
                                          ).props('flat color=white')
                              #TODO find out how to solve authentication problem
                                print(event.ics_url)
                                print(f"{CALDAV_URL}public-calendars/{event.category.public_id}/{event.cloud_id}.ics?export")
                                print(f"{CALDAV_URL}public-calendars/{event.category.public_id}/{event.ics_url.split('/')[-1]}?export")
                    events_ui_list.append(event_item)


        filterUI = Eventfilter(use_filter)
        use_filter()
    
        

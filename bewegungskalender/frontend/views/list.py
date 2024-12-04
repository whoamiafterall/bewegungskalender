# Create Form Page
from slugify import slugify

from bewegungskalender.backend.io.config import MENU
from bewegungskalender.libs.logger import LOGGER
from bewegungskalender.frontend.functions import loading, render_iframe
from bewegungskalender.frontend.navigation.router import ROUTER
from nicegui import events, ui
from nicegui.elements.item import Item
from bewegungskalender.backend.calendar.event import Event
from bewegungskalender.backend.calendar.category import Category

from bewegungskalender.backend.formatting.format import event_time

from nicegui.elements.leaflet import Leaflet
from nicegui.elements.leaflet_layers import Marker
 

from bewegungskalender.frontend.filter import Eventfilter


        
@ROUTER.add(f"/{slugify(str(MENU['list']['label'].lower()))}")
def list_view():
    loading(MENU['list']['label'])



    with (ui.card().classes('w-full min-h-full p-0 m-0') as card):

        with (ui.card().tight().classes('container mx-auto m-10') as card):


            with ui.card().classes('w-full'):
                ui.label('Einige kürzere Termine werden nicht angezeigt. Bearbeite die Filter einstellungen um dies zu ändern.').classes("text-black")


                event_list_ui_element = ui.list().classes('w-full')


        events_ui_list = []

        def use_filter():
            events = filterUI.events_using_filter()
            
            with event_list_ui_element:
                for event_ui in events_ui_list: 
                    event_ui.delete()
                events_ui_list.clear()
                for event in events: 
 
                    events_ui_list.append(ui.item(event.summary).classes("bg-grey w-full mb-2 rounded"))
                

        filterUI = Eventfilter(use_filter)
        use_filter()
    
        

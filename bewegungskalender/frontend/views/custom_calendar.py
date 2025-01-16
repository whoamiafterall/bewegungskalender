from nicegui import ui, events

from bewegungskalender.backend.formatting.nextcloud_urls import NC_YEAR_VIEW
from bewegungskalender.backend.io.config import MENU
from bewegungskalender.libs.logger import LOGGER
from bewegungskalender.frontend.helpers.functions import loading
from bewegungskalender.frontend.navigation.router import ROUTER
from bewegungskalender.frontend.calendar.fullcalendar import FullCalendar

# Create Calendar Page
@ROUTER.add('/calendar2')
async def custom_calendar_view():
    await ui.context.client.connected()
    LOGGER.debug(f"Creating the Calendar View using {NC_YEAR_VIEW}")
    loading(MENU['calendar']['label'])

    options = {
        'initialView': 'dayGridMonth',
        'headerToolbar': {'left': '', 'right': ''},
        'footerToolbar': {'left': 'title','right': 'prev,next today'},
        'slotMinTime': '05:00:00',
        'slotMaxTime': '22:00:00',
        'allDaySlot': False,
        'timeZone': 'local',
        'height': 'auto',
        'width': 'auto',
        'events': []
    }


    def handle_click(event: events.GenericEventArguments):
        if 'info' in event.args:
            ui.notify(event.args['info']['event'])


    FullCalendar(options, on_click=handle_click).add_event(title="test",start="2024-12-04 08:00:00",end="2024-12-04 10:00:00",color='red')


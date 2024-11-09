from nicegui import ui

from bewegungskalender.functions.config import MAIN_MENU
from bewegungskalender.functions.logger import LOGGER
from bewegungskalender.ui.functions import loading, render_iframe
from bewegungskalender.ui.navigation.router import ROUTER

# Create Calendar Page
@ROUTER.add('/')
def calendar_view(right_drawer):
    LOGGER.debug(f"Creating the Calendar View using {MAIN_MENU['calendar']['source']}")
    loading(MAIN_MENU['calendar']['label'])
    render_iframe(MAIN_MENU['calendar']['source'])
    with ui.page_sticky(x_offset=18, y_offset=18):
        ui.button(icon='filter_alt', on_click=lambda: right_drawer.toggle()).props(
            'fab color=accent').classes("sm:hidden")

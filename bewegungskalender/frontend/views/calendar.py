from nicegui import ui

from bewegungskalender.backend.formatting.nextcloud_urls import NC_YEARLY_EMBED
from bewegungskalender.backend.io.config import MENU
from bewegungskalender.libs.logger import LOGGER
from bewegungskalender.frontend.functions import loading, render_iframe
from bewegungskalender.frontend.navigation.router import ROUTER

# Create Calendar Page
@ROUTER.add('/')
def calendar_view():
    LOGGER.debug(f"Creating the Calendar View using {NC_YEARLY_EMBED}")
    loading(MENU['calendar']['label'])
    render_iframe(height='100%', width='100%', source=NC_YEARLY_EMBED)
    with ui.page_sticky(x_offset=18, y_offset=18):
        ui.button(icon='filter_alt', #on_click=lambda: right_drawer.toggle()
            ).props('fab color=accent').classes("sm:hidden")

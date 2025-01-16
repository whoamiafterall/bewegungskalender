# Create About Page
from nicegui import ui
from slugify import slugify

from bewegungskalender.backend.io.config import MENU, STATIC_DIR
from bewegungskalender.libs.logger import LOGGER
from bewegungskalender.frontend.helpers.functions import container
from bewegungskalender.frontend.navigation.router import ROUTER

@ROUTER.add(f"/{slugify(str(MENU['about']['label'].lower()))}")
async def about_view():
    await ui.context.client.connected()
    LOGGER.debug(f"Creating About Panel with the content of {MENU['about']['source']}...")
    with container():
        with open(f"{STATIC_DIR}{MENU['about']['source']}", 'r') as f:  # open file
            with ui.column(align_items='center').classes('w-3/4 mx-auto'):
                ui.markdown(f.read())


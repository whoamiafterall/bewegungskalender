# Create Form Page
from nicegui import ui
from slugify import slugify

from bewegungskalender.backend.io.config import MENU
from bewegungskalender.libs.logger import LOGGER
from bewegungskalender.frontend.helpers.functions import loading
from bewegungskalender.frontend.navigation.router import ROUTER

@ROUTER.add(f"/{slugify(str(MENU['form']['label'].lower()))}")
async def form_view():
    await ui.context.client.connected()
    loading(MENU['form']['label'])
    LOGGER.debug(f"Creating the Form using {MENU['form']['source']}.")
    ui.html(MENU['form']['source']).classes('w-screen h-screen m-0 p-0')
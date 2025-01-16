# Create FAQ Page
from nicegui import ui
from slugify import slugify

from bewegungskalender.backend.io.config import MENU, STATIC_DIR
from bewegungskalender.frontend.helpers.functions import container
from bewegungskalender.frontend.navigation.router import ROUTER


@ROUTER.add(f"/{slugify(str(MENU['FAQ']['label'].lower()))}")
async def faq_view():
    await ui.context.client.connected()
    with container('w-2/3'):
        with open(f"{STATIC_DIR}{MENU['FAQ']['source']}", 'r') as f:  # open file
            ui.html(f.read()).classes('flex-none')

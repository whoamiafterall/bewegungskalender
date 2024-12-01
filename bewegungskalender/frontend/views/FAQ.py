# Create FAQ Page
from nicegui import ui
from slugify import slugify

from bewegungskalender.backend.io.config import MENU, STATIC_DIR
from bewegungskalender.frontend.functions import container
from bewegungskalender.frontend.navigation.router import ROUTER

@ROUTER.add(f"/{slugify(str(MENU['FAQ']['label'].lower()))}")
def faq_view():
    with container():
        with open(f"{STATIC_DIR}{MENU['FAQ']['source']}", 'r') as f:  # open file
            ui.html(f.read()).classes('flex-none')

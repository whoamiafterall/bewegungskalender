# Create FAQ Page
from nicegui import ui
from slugify import slugify

from bewegungskalender.backend.io.config import MAIN_MENU
from bewegungskalender.frontend.functions import container
from bewegungskalender.frontend.navigation.router import ROUTER

@ROUTER.add(slugify(f"/{str(MAIN_MENU['FAQ']['label'].lower())}"))
def faq_view():
    with container():
        with open(MAIN_MENU['FAQ']['source'], 'r') as f:  # open file
            ui.html(f.read()).classes('flex-none')

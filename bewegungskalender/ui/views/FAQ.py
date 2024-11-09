# Create FAQ Page
from nicegui import ui
from slugify import slugify

from bewegungskalender.functions.config import MENU_ITEMS
from bewegungskalender.ui.functions import container
from bewegungskalender.ui.navigation.router import ROUTER

@ROUTER.add(slugify(f"/{str(MENU_ITEMS['FAQ']['label'].lower())}"))
def faq_view():
    with container():
        with open(MENU_ITEMS['FAQ']['source'], 'r') as f:  # open file
            ui.html(f.read()).classes('flex-none')

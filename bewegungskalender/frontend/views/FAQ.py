# Create FAQ Page
from nicegui import ui
from nicegui.elements.mixins.color_elements import color
from slugify import slugify
from sqlmodel import select

from bewegungskalender.backend.calendar.category import Category
from bewegungskalender.backend.io import db
from bewegungskalender.backend.io.config import MENU, STATIC_DIR
from bewegungskalender.frontend.functions import container, opacity, mini_card
from bewegungskalender.frontend.navigation.router import ROUTER


@ROUTER.add(f"/{slugify(str(MENU['FAQ']['label'].lower()))}")
def faq_view():
    
    with container('w-2/3'):
        with open(f"{STATIC_DIR}{MENU['FAQ']['source']}", 'r') as f:  # open file
            ui.html(f.read()).classes('flex-none')

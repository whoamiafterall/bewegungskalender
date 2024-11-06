from contextlib import contextmanager
from typing import Tuple

import yaml
from nicegui import ui
from slugify import slugify

from bewegungskalender.functions.file import safe_open_read
from bewegungskalender.ui.router import Router


@contextmanager
def tab_panel(tab:str):
    with ui.tab_panel(tab).classes('p-0 m-0') as panel:
        yield panel

@contextmanager
def container(classes:str = None):
    with (ui.card().tight().classes(
            'container mx-auto min-h-full overflow-auto p-10 ' # Layout - Trailing White Space is important!
            'bg-black text-base font-light text-secondary') # Text
    as card):
        card.classes(classes) # Add Custom Classes
        yield card

@contextmanager
def render_iframe(source:str): #TODO Add Input Validation - check for <iframe> and url
    ui.html(source).classes('w-screen h-screen p-0 m-0')

@contextmanager
def loading(page_label:str, timeout:float = 0.7):
    ui.notification(f"Lade {page_label}...", position='center', type='ongoing', spinner=True, timeout=timeout)

@contextmanager
def show_links(path):
    with safe_open_read(path) as f:
        links:dict[Tuple[str, str]] = yaml.load(f, Loader=yaml.FullLoader)
        categories:list = []
        for category in links.items():
            with ui.column().classes('h-2/3 mb-5 lg:w-1/4 max-lg:w-1/2 max-sm:w-full'):
                ui.markdown(f"##### {category[0]}")
                categories.append(category[0])
                with ui.scroll_area().classes('w-3/4 items-stretch').props("bar-style={width: '2px'}"):
                    with ui.list().props('dense separator').classes():
                        for item in category[1].items():
                            with ui.item():
                                ui.link(f"{item[0]}", item[1], new_tab=True).classes('font-medium')
        with ui.column().classes('h-full lg:w-1/4 max-lg:w-1/2 max-sm:w-full'):
            ui.markdown("##### Link Hinzufügen")
            ui.select(options=categories, label="Kategorie wählen:", value=categories[0])
            ui.input(label='Stadt/Name:')
         #   ui.input(label='Link:', validation='') #TODO Finish the validation here
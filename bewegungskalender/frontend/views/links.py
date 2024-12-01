from typing import Tuple

import validators
import yaml
from nicegui import ui
from slugify import slugify

from bewegungskalender.backend.io.config import MENU, DATADIR, STATIC_DIR
from bewegungskalender.backend.io.file import safe_open
from bewegungskalender.frontend.functions import ErrorChecker, loading, container
from bewegungskalender.frontend.navigation.router import ROUTER


# Create Links Page
@ROUTER.add(f"/{slugify(str(MENU['links']['label'].lower()))}/")
def links_view():
    loading(MENU['links']['label'], 0.2)
    with container('flex-row flex-wrap'):
        path = f"{STATIC_DIR}{MENU['links']['source']}"
        with safe_open(path, "r") as file:
            links:dict[Tuple[str, str]] = yaml.load(file, Loader=yaml.FullLoader)
            categories:list = []
            for category in links.items():
                with ui.column().classes('h-3/4 mb-5 lg:w-1/4 max-lg:w-1/2 max-sm:w-full'):
                    ui.markdown(f"##### {category[0]}")
                    categories.append(category[0])
                    with ui.scroll_area().classes('w-3/4 items-stretch').props("bar-style={width: '2px'}"):
                        with ui.list().props('dense separator').classes():
                            for item in category[1].items():
                                with ui.item():
                                    ui.link(f"{item[0]}", item[1], new_tab=True).classes('font-medium')
            with ui.column().classes('h-full lg:w-1/4 max-lg:w-1/2 max-sm:w-full'):
                with ui.dialog() as dialog, ui.card():
                    with ui.row():
                        category = ui.select(options=categories, label="Kategorie wählen:", value=categories[0])
                        ui.button(icon='close', on_click=dialog.close).props('flat color=white').classes('h-10 w-10')
                    name = ui.input(label='Stadt/Name:', validation={'Too long!': lambda value: len(value)<50})
                    url = ui.input(label='Link:', validation={'https://example.com/...': lambda value: validators.url(value)})
                    checker = ErrorChecker(name, url)
                    ui.button('Hinzufügen', icon='add', on_click=lambda:
            safe_open(f"{DATADIR}/links_to_moderate.yml", 'a').write(f"{category.value}:\n{name.value}: {url.value}\n")
                              ).on_click(dialog.close).bind_enabled_from(checker, 'no_errors')
                ui.markdown("##### Link Hinzufügen")
                ui.button('Link Hinzufügen', on_click=dialog.open)
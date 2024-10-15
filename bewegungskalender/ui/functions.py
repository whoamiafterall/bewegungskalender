from contextlib import contextmanager
from nicegui import ui

@contextmanager
def tab_panel(tab:str):
    with ui.tab_panel(tab).classes('p-0 m-0') as panel:
        yield panel

@contextmanager
def container(classes:str = None):
    with (ui.card().tight().classes(
            'container mx-auto min-h-full overflow-auto px-10 ' # Layout - Trailing White Space is important!
            'pt-5 bg-black text-base font-light text-secondary') # Text
    as card):
        card.classes(classes) # Add Custom Classes
        yield card

@contextmanager
def my_button_card(text, on_click):
    with ui.button('', on_click=on_click).classes('p-0 rounded'):
        with ui.card().classes('bg-slate-50 hover:bg-slate-100 text-black') as card:
            ui.label('UI elements before')
            yield card  # The remaining code will be executed only after exiting the caller with block
            ui.label(text).classes('w-full items-center text-black')
            ui.label('UI elements after')
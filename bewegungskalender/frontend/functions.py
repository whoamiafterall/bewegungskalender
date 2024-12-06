import math
from contextlib import contextmanager

import validators
from nicegui import ui
from nicegui.elements.mixins.validation_element import ValidationElement
from typing import Callable, Dict, Union

class ErrorChecker:
    def __init__(self, *elements: ValidationElement) -> None:
        self.elements = elements

    @property
    def no_errors(self) -> bool:
        return all(validation(element.value) for element in self.elements for validation in element.validation.values())

@contextmanager
def tab_panel(tab:str):
    with ui.tab_panel(tab).classes('p-0 m-0') as panel:
        yield panel

@contextmanager
def container(classes:str = None):
    with (ui.card().tight().classes(
            'container mx-auto min-h-full overflow-auto px-10 py-5 ' # Layout - Trailing White Space is important!
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

def opacity(percentage:int, color:str):
    alpha = int((percentage / 100)*255)
    color += f'{alpha:02x}'
    return color
from contextlib import contextmanager

from nicegui import ui
from nicegui.elements.mixins.validation_element import ValidationElement


class ErrorChecker:
    def __init__(self, *elements: ValidationElement) -> None:
        self.elements = elements

    @property
    def no_errors(self) -> bool:
        return all(validation(element.value) for element in self.elements for validation in element.validation.values())

@contextmanager
def container(classes:str=None):
    with ui.card(align_items='stretch').tight().props('flat square').classes(
            'min-h-full w-dvw overflow-auto px-4 sm:px-10 rounded-none py-5 ' # Layout - Trailing White Space is important!
            'bg-primary text-base font-light max-sm:mb-[50px] text-secondary') as card: # Text
        card.classes(classes) # Add Custom Classes
        yield card

@contextmanager
def mini_card(classes:str=None):
    with ui.card().tight().classes('m-0 p-2 flex-row bg-primary text-secondary shadow-none items-center ') as card:
        card.classes(classes)
        yield card

@contextmanager
def dropdown_button(name:str, color:str, classes:str=None):
    with ui.dropdown_button(
            text=name,
            color=opacity(70, color),
            auto_close=True,
    ).classes(f"font-normal text-secondary text-sm capitalize grow items-start").props('unelevated') as btn:
        btn.classes(classes)
        yield btn

def icon_link(icon: str, name: str, url: str=None):
    with mini_card('space-x-2 p-1 text-pretty mx-auto'):
        ui.icon(icon, size='20px')
        if url is not None:
            ui.link(name, url, new_tab=True)
        else:
            ui.label(name)

def render_iframe(height:str, width:str, source:str):
    ui.html(f"<iframe src={source} width={width} height={height}></iframe>").classes('w-screen h-screen p-0 m-0')

def loading(page_label:str='', timeout:float = 0.7):
    ui.notification(f"Lade {page_label}...", position='center', type='ongoing', spinner=True, timeout=timeout)

def opacity(percentage:int, color:str):
    alpha = int((percentage / 100)*255)
    color += f'{alpha:02x}'
    return color
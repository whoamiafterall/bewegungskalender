from contextlib import contextmanager

from nicegui import ui
from nicegui.elements.mixins.validation_element import ValidationElement
from nicegui.page_layout import RightDrawer

from bewegungskalender.frontend.navigation.router import ROUTER


class ErrorChecker:
    def __init__(self, *elements: ValidationElement) -> None:
        self.elements = elements

    @property
    def no_errors(self) -> bool:
        return all(validation(element.value) for element in self.elements for validation in element.validation.values())

@contextmanager
def heading(md_string:str):
    with ui.row().classes('justify-center'):
        ui.markdown(md_string).classes('text-center')

@contextmanager
def tab_panel(tab:str):
    with ui.tab_panel(tab).classes('p-0 m-0') as panel:
        yield panel

@contextmanager
def container(classes:str=None):
    with ui.card().tight().props('flat square').classes(
            'container mx-auto min-h-full overflow-auto px-4 sm:px-10 rounded-none py-5 ' # Layout - Trailing White Space is important!
            'bg-primary text-base font-light max-sm:mb-[50px] text-secondary') as card: # Text
        card.classes(classes) # Add Custom Classes
        yield card

def page_sticky(right_drawer: RightDrawer):
    with ui.page_sticky(x_offset=18, y_offset=18).style("z-index: 1000;").bind_visibility_from(ROUTER,"show_filter"):
        ui.button(icon="filter_alt", on_click=lambda:right_drawer.toggle()).props('fab color=accent').classes('sm:hidden')
        
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

def new_tab_icon():
    ui.icon('launch', size='15px').classes('p-[2px]')

def render_iframe(height:str, width:str, source:str):
    ui.html(f"<iframe src={source} width={width} height={height}></iframe>").classes('w-screen h-screen p-0 m-0')

def loading(page_label:str='', timeout:float = 0.7):
    ui.notification(f"Lade {page_label}...", position='center', type='ongoing', spinner=True, timeout=timeout)

def opacity(percentage:int, color:str):
    alpha = int((percentage / 100)*255)
    color += f'{alpha:02x}'
    return color
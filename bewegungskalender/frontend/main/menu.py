from contextlib import contextmanager
from typing import Callable, Any

from nicegui import ui
from nicegui.elements.button import Button
from nicegui.elements.button_group import ButtonGroup
from nicegui.page_layout import LeftDrawer, RightDrawer

from bewegungskalender.backend.io.config import MENU
from bewegungskalender.frontend.navigation.router import ROUTER
from bewegungskalender.frontend.views.FAQ import faq_view
from bewegungskalender.frontend.views.about import about_view
from bewegungskalender.frontend.views.calendar import calendar_view
from bewegungskalender.frontend.views.form import form_view
from bewegungskalender.frontend.views.links import links_view
from bewegungskalender.frontend.views.list import list_view
from bewegungskalender.frontend.views.map import map_view

class MenuButton(Button):
    def __init__(self, item:dict, view:Callable, drawer:LeftDrawer|RightDrawer = None) -> None:
        self.item = item
        self.view = view
        self.drawer = drawer
        super().__init__(item['label'], icon=item['icon'],
            on_click=lambda: self._open_view_close_drawer())
        
    def _open_view_close_drawer(self) -> Any:
        ROUTER.open(self.view)
        if self.drawer:
            self.drawer.hide()
            
def main_menu(left_drawer:LeftDrawer, classes:str=None, props:str=None):
    ui.button(on_click=lambda: left_drawer.toggle(), icon='menu').classes(classes).props(props)
    MenuButton(MENU['list'], list_view).classes(classes).props(props)
    MenuButton(MENU['calendar'], calendar_view).classes(classes).props(props)
#    MenuButton(MENU['calendar'], custom_calendar_view).props(props)
    MenuButton(MENU['map'], map_view).classes(classes).props(props)
  #  MenuButton(MENU['table'], table_view).props(props)

def secondary_menu(left_drawer:LeftDrawer, classes:str=None, props:str=None):
    MenuButton(MENU['form'], form_view, left_drawer).classes(classes).props(props)
    MenuButton(MENU['about'], about_view, left_drawer).classes(classes).props(props)
    MenuButton(MENU['FAQ'], faq_view, left_drawer).classes(classes).props(props)
    MenuButton(MENU['links'], links_view, left_drawer).classes(classes).props(props)
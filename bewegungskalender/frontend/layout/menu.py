from typing import Callable, Any

from nicegui import ui, app
from nicegui.elements.button import Button
from nicegui.page_layout import LeftDrawer, RightDrawer

from bewegungskalender.backend.formatting.nextcloud_urls import NC_MONTH_VIEW, NC_YEAR_VIEW
from bewegungskalender.backend.io.config import MENU
from bewegungskalender.frontend.layout.theme import Theme
from bewegungskalender.frontend.navigation.router import ROUTER
from bewegungskalender.frontend.views.about import about_view
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


class NavigateButton(Button):
    def __init__(self, icon: str, text: str, link: str) -> None:
        super().__init__(text=text, icon=icon, on_click=lambda: ui.navigate.to(link, new_tab=True))


def main_menu(left_drawer:LeftDrawer, classes:str=None, props:str='color=accent text-color=white'):
    MenuButton(MENU['list'], list_view).classes(classes).props(props)
    MenuButton(MENU['map'], map_view).classes(classes).props(props)
    MenuButton(MENU['form'], form_view, left_drawer).classes(classes).props(props)
   # NavigateButton('calendar_month', 'Monat', NC_MONTH_VIEW).classes(classes).props(props)
    NavigateButton('grid_on', 'Jahr', NC_YEAR_VIEW).classes(classes).props(props)
  #  MenuButton(MENU['calendar'], calendar_view).classes(classes).props(props)
#    MenuButton(MENU['calendar'], custom_calendar_view).props(props)
  #  MenuButton(MENU['table'], table_view).props(props)

def secondary_menu(left_drawer:LeftDrawer, classes:str=None, props:str='color=accent text-color=white'):
    MenuButton(MENU['about'], about_view, left_drawer).classes(classes).props(props)
    #MenuButton(MENU['FAQ'], faq_view, left_drawer).classes(classes).props(props)
    MenuButton(MENU['links'], links_view, left_drawer).classes(classes).props(props)
    ui.button(on_click=lambda:Theme.toggle_dark()).classes(classes).props(props).bind_icon_from(app.storage.user,"dark_mode", lambda v: 'dark_mode' if v == False else 'light_mode')#.bind_text_from(Theme,"dark_mode", lambda v: 'Darkmode' if v == False else 'Lightmode')
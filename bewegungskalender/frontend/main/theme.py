from nicegui import ui
from nicegui.elements.dark_mode import DarkMode


class Theme:
    dark_mode:bool = ui.dark_mode().value

    @classmethod
    def toggle_dark(cls):
        if not cls.dark_mode :
            ui.dark_mode(True); cls.dark_mode = True
            ui.query('.nicegui-content').style('background-color:#050505')
            ui.colors(primary='#1c2329', secondary='light-grey', dark='black', accent='#613583')
        else:
            ui.dark_mode(False); cls.dark_mode = False
            ui.query('.nicegui-content').style('background-color:#F5F5E5')
            ui.colors(primary='#E8E8D8', secondary='black', DARK='white', accent='#613583')


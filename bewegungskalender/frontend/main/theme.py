from nicegui import ui, app
from nicegui.elements.dark_mode import DarkMode


class Theme:

    dark_mode: bool = ui.dark_mode().value

    @classmethod
    def load_theme(cls):
        cls.set_dark(app.storage.user.get('dark_mode', True) )

    @classmethod
    def set_dark(cls,value):
        if value:
            ui.dark_mode(True); cls.dark_mode = True; app.storage.user["dark_mode"] = True
        else:
            ui.dark_mode(False); cls.dark_mode = False; app.storage.user["dark_mode"] = False
        cls.apply()

    @classmethod
    def apply(cls):
        if cls.dark_mode:
            ui.query('.nicegui-content').style('background-color:#050505')
            ui.colors(primary='#1c2329', secondary='light-grey', dark='black', accent='#613583')
        else:
            ui.query('.nicegui-content').style('background-color:#F5F5E5')
            ui.colors(primary='#E8E8D8', secondary='black', DARK='white', accent='#613583')

    @classmethod
    def toggle_dark(cls):
        cls.set_dark(cls.dark_mode == False)


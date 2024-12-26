from nicegui import ui, app
from nicegui.elements.dark_mode import DarkMode
from nicegui.events import ValueChangeEventArguments


class Theme:


    @classmethod
    def init_theme(cls):
        ui.dark_mode().bind_value(app.storage.user,"dark_mode").on_value_change(lambda args: apply_dark_mode(args.value))
        apply_dark_mode(cls.is_dark_mode())

    @classmethod
    def set_dark(cls,value):
        app.storage.user["dark_mode"] = value

    @classmethod
    def toggle_dark(cls):
        cls.set_dark(cls.is_dark_mode() == False)

    @classmethod
    def is_dark_mode(cls):
        return app.storage.user.get('dark_mode', True)

def apply_dark_mode(is_dark):

    if is_dark:
        ui.query('.nicegui-content').style('background-color:#050505')
        ui.colors(primary='#1c2329', secondary='light-grey', dark='black', accent='#613583')
    else:
        ui.query('.nicegui-content').style('background-color:#F5F5E5')
        ui.colors(primary='#E8E8D8', secondary='black', DARK='white', accent='#613583')
from nicegui import ui

from bewegungskalender.frontend.functions import container
from bewegungskalender.frontend.main.menu import secondary_menu


def left_drawer():
    with ui.left_drawer(value=False, fixed=True, elevated=True, top_corner=True).classes('p-0 m-0 bg-primary').props(
			'width=auto') as ld:
        with ui.column(wrap=False, align_items='stretch').classes('w-full p-5'):
            secondary_menu(ld, 'bg-accent')
            ui.separator()
            ui.button(icon='close', on_click=lambda: ld.hide()).props('flat color=white align=center').classes(
                'h-24px')
    return ld
    
def right_drawer():
    with ui.right_drawer(value=False, fixed=True, elevated=True, top_corner=True).classes('p-0 m-0').props(
            'width=auto') as rd:
        with container('px-0'):
            with ui.column().classes('items-stretch w-full m-0 p-0'):
                pass
    return rd
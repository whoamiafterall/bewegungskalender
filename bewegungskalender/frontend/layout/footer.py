from nicegui import ui
from nicegui.page_layout import LeftDrawer

from bewegungskalender.frontend.layout.menu import main_menu


def footer(ld:LeftDrawer):
	# Footer is only shown on small screens
	with ui.footer(bordered=True).classes('sm:hidden h-50px flex flex-nowrap items-center fixed p-0 gap-0'):
		main_menu(ld, props='label="" text-color=contrast square', classes='flex-auto bg-accent m-0 p-4')

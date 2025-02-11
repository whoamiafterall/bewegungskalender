from nicegui import ui
from nicegui.page_layout import LeftDrawer, RightDrawer

from bewegungskalender.frontend.layout.menu import main_menu


def footer(ld: LeftDrawer, rd: RightDrawer):
	# Footer is only shown on small screens
	with ui.footer(fixed=True).classes('sm:hidden bg-accent p-2'):
		main_menu(ld, rd, props='label="" flat text-color=contrast', classes='flex-auto bg-accent m-0 p-0')

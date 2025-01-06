from nicegui import ui, app

from bewegungskalender.backend.io.config import UI_TITLE, UI_FAVICON, UI_PORT
from bewegungskalender.backend.io.credentials import UI_STORAGE_SECRET
from bewegungskalender.frontend.functions import page_sticky
from bewegungskalender.frontend.main.drawer import left_drawer, right_drawer
from bewegungskalender.frontend.main.header import header
from bewegungskalender.frontend.main.menu import main_menu
from bewegungskalender.frontend.main.theme import Theme
from bewegungskalender.frontend.navigation.router import ROUTER
from bewegungskalender.libs.logger import LOGGER

@ui.page('/')
@ui.page('/{_:path}')
async def main_page():
    await ui.context.client.connected()

    # Load the theme from browser storage
    Theme.init_theme()

    ui.query('.nicegui-content').classes('p-0 min-h-full overflow-auto') # remove default padding from site
    ROUTER.frame().classes('w-screen h-[calc(100vh-55px)]')
    ld = left_drawer()
    
    rd = await right_drawer()
    header(ld, rd)
    
    with ui.footer(bordered=True).classes('sm:hidden h-50px flex flex-nowrap items-center fixed p-0 gap-0'):
        main_menu(ld, props='label="" text-color=contrast square', classes='flex-auto bg-accent m-0 p-4')
    
    page_sticky(rd)
    
def start_ui():

    LOGGER.debug('Finished. Starting UI...')
    ui.run(title=UI_TITLE, favicon=UI_FAVICON, language='de', port=UI_PORT, uvicorn_logging_level='info',storage_secret=UI_STORAGE_SECRET)

    LOGGER.debug('Successfully started UI.')


# Run as Module or Standalone program
if __name__ in {"__main__", "__mp_main__"}:
    start_ui()
from nicegui import ui

from bewegungskalender.backend.io.config import UI_TITLE, UI_FAVICON, UI_PORT
from bewegungskalender.backend.io.credentials import UI_STORAGE_SECRET
from bewegungskalender.frontend.filter.filter import filter_sticky
from bewegungskalender.frontend.layout.drawer import left_drawer, right_drawer
from bewegungskalender.frontend.layout.footer import footer
from bewegungskalender.frontend.layout.header import header
from bewegungskalender.frontend.layout.theme import Theme
from bewegungskalender.frontend.navigation.router import ROUTER
from bewegungskalender.libs.logger import LOGGER


@ui.page('/')
@ui.page('/{_:path}')
async def main_page():
    await ui.context.client.connected()

    # Load the theme from browser storage
    Theme.init_theme()
    
    # Modify default page container
    ui.query('.nicegui-content').classes('p-0 min-h-full overflow-auto')
    # Create an Invisible frame that shows different views and fits underneath the header / above the footer
    ROUTER.frame().classes('w-screen h-[calc(100vh-55px)]')
    
    # Create visible Layout
    ld = left_drawer()
    rd = await right_drawer()
    header(ld, rd)
    filter_sticky(rd)
    footer(ld)

def start_ui():
    LOGGER.debug('Starting UI...')
    ui.add_head_html('<link rel="manifest" href="/manifest.json">')
    ui.add_head_html(
        '<script>if("serviceWorker" in navigator) { navigator.serviceWorker.register("/service_worker.js"); };</script>')
    ui.run(title=UI_TITLE, favicon=UI_FAVICON, language='de', port=UI_PORT, uvicorn_logging_level='info',storage_secret=UI_STORAGE_SECRET)
    LOGGER.debug('Successfully started UI.')

# Run as Module or Standalone program
if __name__ in {"__main__", "__mp_main__"}:
    start_ui()
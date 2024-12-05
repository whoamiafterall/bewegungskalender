from contextlib import contextmanager

from nicegui import ui, app
from nicegui.page_layout import LeftDrawer

from bewegungskalender.backend.io.config import CONFIG, UI_PORT, UI_FAVICON, UI_TITLE, MENU, ICONS_DIR
from bewegungskalender.frontend.views.table import table_view
from bewegungskalender.libs.logger import LOGGER
from bewegungskalender.frontend.navigation.router import ROUTER
from bewegungskalender.frontend.views.FAQ import faq_view
from bewegungskalender.frontend.views.about import about_view
from bewegungskalender.frontend.views.list import list_view
from bewegungskalender.frontend.views.calendar import calendar_view
from bewegungskalender.frontend.views.form import form_view
from bewegungskalender.frontend.views.links import links_view
from bewegungskalender.frontend.views.map import map_view
from bewegungskalender.frontend.views.custom_calendar import custom_calendar_view


app.add_static_files(CONFIG['assets']['url_path'], ICONS_DIR)


@contextmanager
def theme():
    ui.query('.nicegui-content').classes('p-0')  # remove default padding from site
    ui.dark_mode(False)  # Set dark mode
    ui.colors(primary='#1c2329', secondary='white', accent='green')

@contextmanager
def header(left_drawer:LeftDrawer):
    with ui.header(elevated=True).classes('fixed h-50px m-0 px-3 py-2 items-center'):
        ui.button(on_click=lambda: left_drawer.toggle(), icon='menu').props('flat color=white').classes('lg:hidden')
        main_menu()
        ui.space().classes('max-sm:hidden')
        with ui.row().classes('max-lg:hidden m-0 p-0'):
            secondary_menu()
        ui.space().classes('max-sm:hidden')

@contextmanager
def main_menu():
    with ui.button_group().props('flat'):
        ui.button(MENU['list']['label'], icon=MENU['list']['icon'],
                  on_click=lambda: ROUTER.open(list_view))
        ui.button(MENU['calendar']['label'], icon=MENU['calendar']['icon'],
                  on_click=lambda: ROUTER.open(calendar_view))
        ui.button(MENU['calendar']['label']+" Test", icon=MENU['calendar']['icon'],
                  on_click=lambda: ROUTER.open(custom_calendar_view))
        ui.button(MENU['map']['label'], icon=MENU['map']['icon'],
                  on_click=lambda: ROUTER.open(map_view))
        ui.button(MENU['table']['label'], icon=MENU['table']['icon'],
                  on_click=lambda: ROUTER.open(table_view))
@contextmanager
def secondary_menu():
    with ui.button_group().props('outline rounded'):
        ui.button(MENU['form']['label'], icon=MENU['form']['icon'],
                  on_click=lambda: ROUTER.open(form_view))
        ui.button(MENU['about']['label'], icon=MENU['about']['icon'],
                  on_click=lambda: ROUTER.open(about_view))
        ui.button(MENU['FAQ']['label'], icon=MENU['FAQ']['icon'],
                  on_click=lambda: ROUTER.open(faq_view))
        ui.button(MENU['links']['label'], icon=MENU['links']['icon'],
                  on_click=lambda: ROUTER.open(links_view))

@contextmanager
def left_drawer():
    with ui.left_drawer(value=False, fixed=True, elevated=True).classes('lg:hidden background-primary p-0 m-0').props(
            'width=auto persistent=False') as left_drawer:
        ui.space()
        with ui.column(wrap=False, align_items='stretch').classes('w-full p-5'):
            ui.button(MENU['form']['label'], icon=MENU['form']['icon'],
                      on_click=lambda: ROUTER.open(form_view)).on_click(lambda: left_drawer.hide())
            ui.button(MENU['about']['label'], icon=MENU['about']['icon'],
                      on_click=lambda: ROUTER.open(about_view)).on_click(lambda: left_drawer.hide())
            ui.button(MENU['FAQ']['label'], icon=MENU['FAQ']['icon'],
                      on_click=lambda: ROUTER.open(faq_view)).on_click(lambda: left_drawer.hide())
            ui.button(MENU['links']['label'], icon=MENU['links']['icon'],
                      on_click=lambda: ROUTER.open(links_view)).on_click(lambda: left_drawer.hide())
            ui.separator()
            ui.button(icon='close', on_click=lambda: left_drawer.hide()).props('flat color=white align=center').classes(
                'h-24px')
    return left_drawer


#nice gui support async function for page loading
@ui.page('/')
@ui.page('/{_:path}')
async def main_page():
    await ui.context.client.connected()
    theme()
    ld = left_drawer()
    header(ld)

    ROUTER.frame().classes('w-screen h-[calc(100vh-50px)] mt-50')

    # Create One List View for each Category (Calendar) #TODO #FIXME
    #  for calendar in data:
    #     LOGGER.debug(f"Adding List View of {calendar.name} to UI...")
    #    if calendar.events != []:
    #       with frontend.tab_panel(calendar.name):
    #          frontend.html(message.html)


# storage_secret = ''.join(random.SystemRandom().choice(string.ascii_letters + string.digits) for _ in range(32))

#seperate start_ui out from main page
def start_ui():

    LOGGER.debug('Finished. Starting UI...')
    ui.run(title=UI_TITLE, favicon=UI_FAVICON, port=UI_PORT)  #storage_secret=storage_secret)
    LOGGER.debug('Successfully started UI.')
    # add static files

from nicegui import ui, app

from bewegungskalender.functions.config import CONFIG, UI_PORT, UI_FAVICON, UI_TITLE, MAIN_MENU
from bewegungskalender.functions.logger import LOGGER
from bewegungskalender.ui.functions import container
from bewegungskalender.ui.views.FAQ import faq_view
from bewegungskalender.ui.views.about import about_view
from bewegungskalender.ui.views.calendar import calendar_view
from bewegungskalender.ui.views.form import form_view
from bewegungskalender.ui.views.links import links_view
from bewegungskalender.ui.views.map import map_view
from bewegungskalender.ui.navigation.router import ROUTER


#nice gui support async function for page loading
@ui.page('/')
@ui.page('/{_:path}')
async def main_page():
    ui.query('.nicegui-content').classes('p-0')  # remove default padding from site
    ui.dark_mode(True)  # Set dark mode
    ui.colors(primary='#1c2329', secondary='white', accent='green')

    with ui.right_drawer(value=False, fixed=True, elevated=True, top_corner=True).classes('p-0 m-0').props(
            'width=auto') as right_drawer:
        with container('px-0'):
            with ui.column().classes('items-stretch w-full m-0 p-0'):
                pass

    with ui.header(elevated=True).classes('fixed h-50px m-0 px-3 py-2 items-center'):
        with ui.button_group().props('flat'):
            ui.button(on_click=lambda: left_drawer.toggle(), icon='menu').props('flat color=white').classes('lg:hidden')
            ui.button(MAIN_MENU['calendar']['label'], icon=MAIN_MENU['calendar']['icon'],
                      on_click=lambda: ROUTER.open(calendar_view))
            ui.button(MAIN_MENU['map']['label'], icon=MAIN_MENU['map']['icon'],
                      on_click=lambda: ROUTER.open(map_view))
        ui.space().classes('max-sm:hidden')
        with ui.row().classes('max-lg:hidden m-0 p-0'):
            with ui.button_group().props('outline rounded'):
                ui.button(MAIN_MENU['form']['label'], icon=MAIN_MENU['form']['icon'],
                          on_click=lambda: ROUTER.open(form_view))
                ui.button(MAIN_MENU['about']['label'], icon=MAIN_MENU['about']['icon'],
                          on_click=lambda: ROUTER.open(about_view))
                ui.button(MAIN_MENU['FAQ']['label'], icon=MAIN_MENU['FAQ']['icon'],
                          on_click=lambda: ROUTER.open(faq_view))
                ui.button(MAIN_MENU['links']['label'], icon=MAIN_MENU['links']['icon'],
                          on_click=lambda: ROUTER.open(links_view))
        ui.space().classes('max-sm:hidden')
        ui.button("Filter", icon='filter_alt', on_click=lambda: right_drawer.toggle()).props(
            'flat color=white').classes('max-sm:hidden')

    with ui.left_drawer(value=False, fixed=True, elevated=True).classes('lg:hidden background-primary p-0 m-0').props(
            'width=auto persistent=False') as left_drawer:
        ui.space()
        with ui.column(wrap=False, align_items='stretch').classes('w-full p-5'):
            ui.button(MAIN_MENU['form']['label'], icon=MAIN_MENU['form']['icon'],
                      on_click=lambda: ROUTER.open(form_view)).on_click(lambda: left_drawer.hide())
            ui.button(MAIN_MENU['about']['label'], icon=MAIN_MENU['about']['icon'],
                      on_click=lambda: ROUTER.open(about_view)).on_click(lambda: left_drawer.hide())
            ui.button(MAIN_MENU['FAQ']['label'], icon=MAIN_MENU['FAQ']['icon'],
                      on_click=lambda: ROUTER.open(faq_view)).on_click(lambda: left_drawer.hide())
            ui.button(MAIN_MENU['links']['label'], icon=MAIN_MENU['links']['icon'],
                      on_click=lambda: ROUTER.open(links_view)).on_click(lambda: left_drawer.hide())
            ui.separator()
            ui.button(icon='close', on_click=lambda: left_drawer.hide()).props('flat color=white align=center').classes(
                'h-24px')

    ROUTER.frame().classes('w-screen h-[calc(100vh-50px)] mt-50')

    # Create One List View for each Category (Calendar) #TODO #FIXME
    #  for calendar in data:
    #     LOGGER.debug(f"Adding List View of {calendar.name} to UI...")
    #    if calendar.events != []:
    #       with ui.tab_panel(calendar.name):
    #          ui.html(message.html)


# storage_secret = ''.join(random.SystemRandom().choice(string.ascii_letters + string.digits) for _ in range(32))

#seperate start_ui out from main page
def start_ui():
    LOGGER.debug('Finished. Starting UI...')
    ui.run(title=UI_TITLE, favicon=UI_FAVICON, port=UI_PORT)  #storage_secret=storage_secret)
    LOGGER.debug('Successfully started UI.')
    # add static files
    app.add_static_files(CONFIG['assets']['url_path'], CONFIG['assets']['local_dir'])

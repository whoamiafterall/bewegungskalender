from nicegui import ui, app
from slugify import slugify

from bewegungskalender.functions.config import CONFIG, UI_PORT, UI_FAVICON, UI_TITLE, MAP_ZOOM, MAP_CENTER_LAT, \
    MAP_CENTER_LON, MENU_ITEMS
from bewegungskalender.functions.logger import LOGGER
from bewegungskalender.static.history import history
from bewegungskalender.ui.functions import container, render_iframe, loading
from bewegungskalender.ui.links import show_links
from bewegungskalender.ui.map import configure_map
from bewegungskalender.ui.router import Router


#nice gui support async function for page loading
@ui.page('/')
@ui.page('/{_:path}')
async def main_page():
    ui.query('.nicegui-content').classes('p-0') # remove default padding from site
    ui.dark_mode(True) # Set dark mode
    ui.colors(primary='#1c2329', secondary='white', accent='green')
    router = Router()

    # Create Calendar Page
    @router.add('/')
    def calendar():
        LOGGER.debug(f"Creating the Calendar View using {MENU_ITEMS['calendar']['source']}")
        loading(MENU_ITEMS['calendar']['label'])
        render_iframe(MENU_ITEMS['calendar']['source'])
        with ui.page_sticky(x_offset=18, y_offset=18):
            ui.button(icon='filter_alt', on_click=lambda: right_drawer.toggle()).props(
                'fab color=accent').classes("sm:hidden")

    # Create Map View
    @router.add(slugify(f"/{str(MENU_ITEMS['map']['label'].lower())}"))
    async def event_map():
        loading(MENU_ITEMS['map']['label'])
        LOGGER.debug('Creating the Map to show events...')
        # new leaflet with center set to center of germany
        with ui.leaflet(center=(MAP_CENTER_LAT, MAP_CENTER_LON), zoom=MAP_ZOOM).classes('w-full h-full') as leaflet:
            with ui.page_sticky(x_offset=18, y_offset=18).classes('sm:hidden z-5000'): #TODO Fix (it's not shown for whatever reason)
                ui.button(icon='filter_alt', on_click=lambda: right_drawer.toggle()).props(
                    'fab color=accent')
        await configure_map(leaflet)

    # Create Form Page
    @router.add(slugify(f"/{str(MENU_ITEMS['form']['label'].lower())}"))
    def form():
        loading(MENU_ITEMS['form']['label'])
        LOGGER.debug(f"Creating the Form using {MENU_ITEMS['form']['source']}.")
        render_iframe(MENU_ITEMS['form']['source'])

    # Create About Page
    @router.add(slugify(f"/{str(MENU_ITEMS['about']['label'].lower())}"))
    def about():
        LOGGER.debug(f"Creating About Panel with the content of {MENU_ITEMS['about']['source']}...")
        with container('md:w-2/3'):
            with open(MENU_ITEMS['about']['source'], 'r') as f:  # open file
                ui.markdown(f.read())
            history()

    # Create FAQ Page
    @router.add(slugify(f"/{str(MENU_ITEMS['FAQ']['label'].lower())}"))
    def faq():
        with container():
            with open(MENU_ITEMS['FAQ']['source'], 'r') as f:  # open file
                ui.html(f.read()).classes('flex-none')

    # Create Links Page
    @router.add(slugify(f"/{str(MENU_ITEMS['links']['label'].lower())}"))
    def links():
        loading(MENU_ITEMS['links']['label'], 0.2)
        with container('flex-row flex-wrap'):
            show_links()

    with ui.right_drawer(value=False, fixed=True, elevated=True, top_corner=True).classes('p-0 m-0').props(
            'width=auto') as right_drawer:
        with container('px-0'):
            with ui.column().classes('items-stretch w-full m-0 p-0'):
                pass

    with ui.header(elevated=True).classes('fixed h-50px m-0 px-3 py-2 items-center'):
        with ui.button_group().props('flat'):
            ui.button(on_click=lambda:left_drawer.toggle(), icon='menu').props('flat color=white').classes('lg:hidden')
            ui.button(MENU_ITEMS['calendar']['label'], icon=MENU_ITEMS['calendar']['icon'],
                      on_click=lambda: router.open(calendar))
            ui.button(MENU_ITEMS['map']['label'], icon=MENU_ITEMS['map']['icon'],
                      on_click=lambda: router.open(event_map))
        ui.space().classes('max-sm:hidden')
        with ui.row().classes('max-lg:hidden m-0 p-0'):
            with ui.button_group().props('outline rounded'):
                ui.button(MENU_ITEMS['form']['label'], icon=MENU_ITEMS['form']['icon'],
                          on_click=lambda: router.open(form))
                ui.button(MENU_ITEMS['about']['label'], icon=MENU_ITEMS['about']['icon'],
                          on_click=lambda: router.open(about))
                ui.button(MENU_ITEMS['FAQ']['label'], icon=MENU_ITEMS['FAQ']['icon'],
                          on_click=lambda: router.open(faq))
                ui.button(MENU_ITEMS['links']['label'], icon=MENU_ITEMS['links']['icon'],
                          on_click=lambda: router.open(links))
        ui.space().classes('max-sm:hidden')
        ui.button("Filter", icon='filter_alt', on_click=lambda:right_drawer.toggle()).props('flat color=white').classes('max-sm:hidden')

    with ui.left_drawer(value=False, fixed=True, elevated=True).classes('lg:hidden background-primary p-0 m-0').props('width=auto persistent=False') as left_drawer:
        ui.space()
        with ui.column(wrap=False, align_items='stretch').classes('w-full p-5'):
            ui.button(MENU_ITEMS['form']['label'], icon=MENU_ITEMS['form']['icon'],
                      on_click=lambda: router.open(form)).on_click(lambda:left_drawer.hide())
            ui.button(MENU_ITEMS['about']['label'], icon=MENU_ITEMS['about']['icon'],
                      on_click=lambda: router.open(about)).on_click(lambda:left_drawer.hide())
            ui.button(MENU_ITEMS['FAQ']['label'], icon=MENU_ITEMS['FAQ']['icon'],
                      on_click=lambda: router.open(faq)).on_click(lambda:left_drawer.hide())
            ui.button(MENU_ITEMS['links']['label'], icon=MENU_ITEMS['links']['icon'],
                      on_click=lambda:router.open(links)).on_click(lambda:left_drawer.hide())
            ui.separator()
            ui.button(icon='close', on_click=lambda:left_drawer.hide()).props('flat color=white align=center').classes('h-24px')

    router.frame().classes('w-screen h-[calc(100vh-50px)] mt-50')

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
    ui.run(title=UI_TITLE, favicon=UI_FAVICON, port=UI_PORT) #storage_secret=storage_secret)
    LOGGER.debug('Successfully started UI.')
    # add static files
    app.add_static_files(CONFIG['assets']['url_path'], CONFIG['assets']['local_dir'])  







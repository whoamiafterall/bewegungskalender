from nicegui import ui, app
from bewegungskalender.functions.config import CONFIG
from bewegungskalender.functions.logger import LOGGER
from bewegungskalender.ui.functions import tab_panel, container
from bewegungskalender.ui.map import configure_map


#nice gui support async function for page loading
@ui.page('/')
async def main_page():
    ui.query('.nicegui-content').classes('p-0') # remove default padding from site
    ui.dark_mode(True) # Set dark mode
    ui.colors(primary='#1c2329', secondary='white')
    
    # Create Tabs
    LOGGER.debug('Creating Tabs...')
    with ui.header().classes('fixed p-0 m-0') as header:
        with ui.tabs().classes('w-full') as tabs:
            home = ui.tab(name='main_page', label=CONFIG['main_page']['label'], icon='home')
            calendar = ui.tab(name='all_events', label=CONFIG['all_events']['label'], icon='calendar_month')
            # Create one Tab for each Category (Calendar)
          #  for calendar in data:
           #     if calendar.events != []:
           #         ui.tab(calendar.name)
            # Create one Tab for the Map
            ui.tab(CONFIG['map']['label'], icon='map')
            # Create one tab for the Form
            form = ui.tab(name='form', label=CONFIG['form']['label'], icon='edit_calendar')
            faq = ui.tab(name='legende', label=CONFIG['legende']['label'], icon='question_mark')
            links = ui.tab(name='links', label=CONFIG['links']['label'], icon='link')
    
    # Create Tab Panels (what is shown when Tab is selected)
    LOGGER.debug('Creating Tab Panels (Content)...')

    with ui.card().classes('w-screen h-dvh p-0'):
        with ui.tab_panels(tabs, value=home).classes('w-full h-full fixed'):

            # Create one Tab for displaying Homepage
            LOGGER.debug(f"Creating Help Panel with the content of {CONFIG['main_page']['path']}...")
            with tab_panel(home):
                    with container('w-2/3'):
                        with open(CONFIG['main_page']['path'], 'r') as f: # open file
                            ui.markdown(f.read())

            # Create Calendar Page
            LOGGER.debug('Creating the List showing All Events...')
            with tab_panel(calendar):
                ui.html(CONFIG['all_events']['iframe']).classes('w-screen h-screen p-0 m-0')

            # Create Form Page
            LOGGER.debug('Creating the Form to enter a new event...')
            with tab_panel(form):
                ui.html(CONFIG['form']['iframe']).classes('w-screen h-screen p-0 m-0')

            # Create FAQ Page
            with tab_panel(faq):
                with container():
                    with open(CONFIG['legende']['path'], 'r') as f:  # open file
                        ui.html(f.read()).classes('flex-none')
                    with open(CONFIG['FAQ']['path'], 'r') as f:  # open file
                        ui.markdown(f.read()).classes('flex-initial')

            # Create Links Page
            with tab_panel(links):
                with container():
                    with open(CONFIG['links']['path'], 'r') as f:  # open file
                        ui.markdown(f.read()).classes('w-full pt-5')

            # Create Map View
            LOGGER.debug('Creating the Map to show events...')
            with ui.tab_panel(CONFIG['map']['label']).classes('p-0 m-0'):                      
                # new map with center set to center of germany
                map = ui.leaflet(center=(CONFIG['map']['center']['lat'], CONFIG['map']['center']['lon']), zoom=CONFIG['map']['zoom']).classes('w-screen h-screen p-0 m-0')
                map = await configure_map(map)



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
    ui.run(title=CONFIG['title'], favicon=CONFIG['favicon'], port=CONFIG['port'], on_air=True) #storage_secret=storage_secret)
    LOGGER.debug('Successfully started UI.')
    # add static files
    app.add_static_files(CONFIG['assets']['url_path'], CONFIG['assets']['local_dir'])  








from typing import NamedTuple
from nicegui import ui, app
from logging import debug
from bewegungskalender.helper.config import config
from bewegungskalender.output.message import MultiFormatMessage
from bewegungskalender.ui.helper.map import configure_map

#nice gui support async function for page loading
@ui.page('/')
async def main_page():
    ui.query('.nicegui-content').classes('p-0') # remove default padding from site
    ui.dark_mode(True) # Set dark mode
    ui.colors(primary='#1c2329', secondary='white')
    
    # Create Tabs
    debug('Creating Tabs...')
    with ui.header().classes('fixed p-0 m-0') as header:
        with ui.tabs().classes('w-full') as tabs:
            # Create one Tab for showing Help
            help = ui.tab(name='help', label=config['help']['label'], icon='home')
            # Create one Tab for showing All Events in a List
            all_events = ui.tab(name='all_events', label=config['all_events']['label'], icon='calendar_month')
            # Create one Tab for each Category (Calendar)
          #  for calendar in data:
           #     if calendar.events != []:
           #         ui.tab(calendar.name)   
            # Create one Tab for the Map
            ui.tab(config['map']['label'], icon='map')
            # Create one tab for the Form
            form = ui.tab(name='form', label=config['form']['label'], icon='edit_calendar')
                
    
    # Create Tab Panels (what is shown when Tab is selected)
    debug('Creating Tab Panels (Content)...')
    with ui.card().classes('w-screen h-dvh p-0'):
        with ui.tab_panels(tabs, value=help).classes('w-full h-full fixed'):
            # Create one Tab for displaying help
            debug(f"Creating Help Panel with the content of {config['help']['path']}...")
            with ui.tab_panel(help).classes('p-0 m-0'):                
                with ui.row().classes('w-screen h-dvh gap-0 p-0 m-0'):
                    with ui.card().tight().classes('md:w-1/2 w-full md:h-full pl-10 pr-10 pb-20 m-0 bg-black text-base anitaliased font-light text-secondary decoration-primary'):
                        with open(config['help']['path'], 'r') as f: # open file 
                            ui.markdown(f.read())
                    with ui.card().tight().classes('md:w-1/2 w-full md:h-full pl-10 pr-10 pb-20 m-0 bg-black text-base anitaliased font-light text-secondary'):
                        with open(config['legende']['path'], 'r') as f: # open file 
                            ui.markdown("#### Kategorien erklärt ℹ️")
                            ui.html(f.read()).classes('w-full pt-5')
            
            # Create one Grid for displaying everything
            debug('Creating the List showing All Events...')
            with ui.tab_panel(all_events).classes('p-0 m-0'):
                ui.html(config['all_events']['iframe']).classes('w-screen h-screen p-0 m-0')
                        
            # Create Form View
            debug('Creating the Form to enter a new event...')
            with ui.tab_panel(form).classes('p-0 m-0'):
                ui.html(config['form']['iframe']).classes('w-screen h-screen p-0 m-0')
            
            # Create Map View
            debug('Creating the Map to show events...')
            with ui.tab_panel(config['map']['label']).classes('p-0 m-0'):                      
                # new map with center set to center of germany
                map = ui.leaflet(center=(config['map']['center']['lat'], config['map']['center']['lon']), zoom=config['map']['zoom']).classes('w-screen h-screen p-0 m-0')
                map = await configure_map(map)
            
                
                 # Create One List View for each Category (Calendar) #TODO #FIXME
          #  for calendar in data:
           #     debug(f"Adding List View of {calendar.name} to UI...")
            #    if calendar.events != []:
             #       with ui.tab_panel(calendar.name):
              #          ui.html(message.html)   

   # storage_secret = ''.join(random.SystemRandom().choice(string.ascii_letters + string.digits) for _ in range(32))

#seperate start_ui out from main page
def start_ui():
    debug('Finished. Starting UI...')
    ui.run(title=config['title'], favicon=config['favicon'], port=config['port']) #storage_secret=storage_secret)
    debug('Successfully started UI.')
    # add static files
    app.add_static_files(config['assets']['url_path'], config['assets']['local_dir'])  


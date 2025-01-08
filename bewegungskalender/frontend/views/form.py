# Create Form Page
from datetime import datetime

from nicegui import ui
from slugify import slugify

from bewegungskalender.backend.io.config import MENU
from bewegungskalender.frontend.functions import container, mini_card
from bewegungskalender.frontend.navigation.router import ROUTER


@ROUTER.add(f"/{slugify(str(MENU['form']['label'].lower()))}")
async def form_view():
    await ui.context.client.connected()
    # loading(MENU['form']['label'])
    #LOGGER.debug(f"Creating the Form using {MENU['form']['source']}.")
    #ui.html(MENU['form']['source']).classes('w-screen h-screen m-0 p-0')
    
    summary:str = "Mein Event"
    
    
    with container('flex-column'):
        classes = "grow text-sm font-medium color-accent bg-primary items-center justify-between"
        with mini_card(classes):
            ui.space()
            ui.markdown("### Termin eintragen").classes('grow')
        
        with ui.stepper().props('vertical inactive-color=accent active-color=accent flat done-color=positive').classes(classes) as stepper:
        
        # ---- First Step -------
            with ui.step('Start & Ende (1/10)', icon='date_range'):
                ui.label("Klicke zuerst auf das Startdatum, dann auf das Enddatum und gib dann die Start-Zeit an, falls die Uhr erscheint :)")
                with ui.row().classes('flex-row'):
                    date_range = ui.date(value='today', mask='DD.MM.YY'
                         ).props(f"range minimal color=accent flat navigation-min-year-month=2024/12 navigation-max-year-month=2026/12")
                    #ToDo set the minimum possible value to the current month and the maximum possible value to in 2 years
                    start_time = ui.time(value=f"{datetime.now().time():%H %M}"
                        ).props(f'color=accent minimal flat format24h :hour-options="[1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23]" :minute-options="[0,15,30,45]" options=""'
                        ).bind_visibility(date_range, 'value') #forward=lambda v: True if v['from']-v['to']<1 else False)
                with ui.stepper_navigation():
                    ui.button('Next', on_click=stepper.next)
            
        # ----- Second Step -------
            with ui.step('Titel & Beschreibung (2/10)', icon='label_important'):
                with mini_card('column w-full'):
                    title = ui.input('Veranstaltungstitel (*)', placeholder='Min. 5, Max. 60 Zeichen', validation={
                        'Zu lang!': lambda value: len(value) < 60,
                        'Zu kurz!': lambda value: len(value) > 5
                    }).classes(classes)
                    description = ui.textarea('Eine genauere Beschreibung der Veranstaltung (*)', placeholder="Maximal 400 Zeichen.",
                                validation={'Zu lang!': lambda value: len(value) < 400
                    }).on('keydown.enter', lambda: stepper.next() if description.validate() and title.validate() else ui.notify("Not Valid!", type='warning')).classes(classes)

        # ----- Third Step -------
            with ui.step('Link & Adresse (2/10)'):
                with mini_card('column w-full'):
                    ui.label("Gerne ein Post auf eurer Website oder ein Social Media Post. Bitte direkt den Post verlinken - z.B. https://www.instagram.com/p/abcdef/").classes(classes)
                    link = ui.input('Ein Link mit den wichtigsten Informationen (*)', placeholder='https://', validation={
                        'Der Link muss mit https:// beginnen!': lambda value: str(value).startswith('https://')
                    }).on('keydown.enter', lambda: stepper.next() if link.validate() else ui.notify("Not Valid!", type='warning')).classes(classes)
                    location = ui.input('Ein Link mit den wichtigsten Informationen (*)', placeholder='https://', validation={
                        'Der Link muss mit https:// beginnen!': lambda value: str(value).startswith('https://')
                    }).on('keydown.enter', lambda: stepper.next() if link.validate() else ui.notify("Not Valid!", type='warning')).classes(classes)

            with ui.stepper_navigation():
                ui.button('Done', on_click=lambda: ui.notify('Yay!', type='positive'))
#        with ui.step('Link (3/10)'):


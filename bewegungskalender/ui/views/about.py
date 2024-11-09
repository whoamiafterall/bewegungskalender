# Create About Page
from nicegui import ui
from slugify import slugify

from bewegungskalender.functions.config import MENU_ITEMS
from bewegungskalender.functions.logger import LOGGER
from bewegungskalender.ui.functions import container
from bewegungskalender.ui.navigation.router import ROUTER

@ROUTER.add(slugify(f"/{str(MENU_ITEMS['about']['label'].lower())}"))
def about_view():
    LOGGER.debug(f"Creating About Panel with the content of {MENU_ITEMS['about']['source']}...")
    with container('md:w-2/3'):
        with open(MENU_ITEMS['about']['source'], 'r') as f:  # open file
            ui.markdown(f.read())
        history()

def history(): #TODO Complete this and load the content from a static file
    ui.markdown('### Geschichte des Bewegungskalenders')
    with ui.timeline(side='right'):
        ui.timeline_entry(
            'Zwei Menschen hatten die Idee einen bewegungsübergreifenden Kalender für Camps und andere Termine zu erstellen.',
            title='Erste Idee',
            subtitle='Januar, 2023')
        ui.timeline_entry(
            'Der erste Schritt war schnell getan, ein https://systemli.org Konto wurde angelegt, und Termine eingetragen.',
            title='Erster Schritt',
            subtitle='Februar, 2023')
        ui.timeline_entry(
            'Eins davon fing an einen Telegram Bot zu schreiben, der eine automatisierte Nachricht schickt.',
            title='Telegram Bot',
            subtitle='März, 2023')
        ui.timeline_entry(
            'Ein anderer Mensch hatte von dem Projekt gehört und angeboten eine Webseite auf https://klimax.online/bewegungskalender zu erstellen.',
            title='Erste Website',
            subtitle='April, 2023',
            icon='web')
        ui.timeline_entry(
            'Two peeps started working on the new webpage, which is now 100% self-made based on the https://nicegui.io framework.',
            title='New self-made Website',
            subtitle='September, 2024',
            icon='rocket')

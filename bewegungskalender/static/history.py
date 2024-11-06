from contextlib import contextmanager

from nicegui import ui


@contextmanager
def history(): #TODO Complete this
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

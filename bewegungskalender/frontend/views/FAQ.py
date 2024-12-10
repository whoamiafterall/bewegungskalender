# Create FAQ Page
from bewegungskalender.backend.formatting.nextcloud_urls import NC_MONTHLY_VIEW, NC_LIST_VIEW
from calendar import month

from nicegui import ui
from slugify import slugify
from sqlmodel import select

from bewegungskalender.backend.calendar.category import Category
from bewegungskalender.backend.io import db
from bewegungskalender.backend.io.config import MENU, STATIC_DIR
from bewegungskalender.backend.io.credentials import NC_DOMAIN
from bewegungskalender.frontend.functions import container, opacity, mini_card
from bewegungskalender.frontend.navigation.router import ROUTER

@ROUTER.add(f"/{slugify(str(MENU['FAQ']['label'].lower()))}")
def faq_view():
    categories = db.exe(select(Category)).all()
   # public_ids =[category.public_id for category in categories]
    
    with (container()):
        # Create Buttons applying to the whole project
        with mini_card('space-x-2'):
            ui.button(text='Monatsansicht', icon='calendar_month',
                      on_click=lambda: ui.navigate.to(
                          NC_MONTHLY_VIEW, new_tab=True)
                      ).props('flat color=white').classes('font-normal hover:font-medium normal-case')
        with mini_card('space-x-2'):
            ui.button(text='Listenansicht', icon='calendar_view_day',
                      on_click=lambda: ui.navigate.to(
                          NC_LIST_VIEW, new_tab=True)
                      ).props('flat color=white').classes('font-normal hover:font-medium normal-case')
        
        # Create Buttons with useful Information and Links for each Category
        for category in categories:
            with ui.column():
                
                # Create the summary dropdown button
                with ui.dropdown_button(
                        text=category.name,
                        color=opacity(60, category.color),
                        auto_close=True
                ).classes(
                    'font-normal text-sm sm:text-base capitalize hover:font-medium max-sm:w-full grow items-start'):
                    
                    # Create the dropdown content
                    with mini_card('flex-col text-sm w-full'):
                        with mini_card('space-x-2'):
                            ui.label(category.description).classes('text-balance text-center')
                        with mini_card('space-x-2'):
                            ui.icon('map', size='20px')
                        # ui.link(event.link, event.link, new_tab=True)
                        with mini_card('space-x-2'):
                            ui.button(text='Copy subscribe link', icon='content_copy',
                                      on_click=lambda: ui.clipboard.write(category.ics_url)
                            ).props('flat color=white').classes('font-normal hover:font-medium normal-case')
                        with mini_card('space-x-2'):
                            ui.button(text='How to Subscribe', icon='lightbulb', #TODO Add the How to to aktivismus.org
                                      on_click=lambda: ui.navigate.to('https://pad.kanthaus.online/Nextcloud?both=#Subscribe-to-Calendars', new_tab=True)
                            ).props('flat color=white').classes('font-normal hover:font-medium normal-case')
            
            print(category.internal)
        
        
        with open(f"{STATIC_DIR}{MENU['FAQ']['source']}", 'r') as f:  # open file
            ui.html(f.read()).classes('flex-none')

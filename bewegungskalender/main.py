# external imports
import asyncio
import locale
from locale import setlocale

from bewegungskalender.backend.calendar.category import Category
# internal imports
from bewegungskalender.backend.io.cli import FORMAT, ARGS
from bewegungskalender.libs.logger import LOGGER
from bewegungskalender.backend.io.config import LOCALE, CALENDARS
from bewegungskalender.backend.io.nextcloud_forms import update_ncform
from bewegungskalender.backend.calendar.client import get_upcoming_events
from bewegungskalender.backend.formatting.message import MultiFormatMessage, create_message
from bewegungskalender.backend.output.telegram_bot import get_telegram_updates, send_or_edit_telegram
from bewegungskalender.backend.output.map_data import create_mapdata
from bewegungskalender.backend.output.mail import send_mail
from bewegungskalender.frontend.main_frame import start_ui

# Set locale
LOGGER.info(f"Args: {ARGS}")
LOGGER.debug('Setting locale...')
setlocale(locale.LC_ALL, LOCALE)

# Main Function if run as standalone program
def main():
    # frontend.run can't be called from async call
    if ARGS.user_interface: 
        LOGGER.info("Starting User Interface!")
        start_ui()
    else:
        asyncio.run(main_async())

# Main async function call if not running NiceGui
async def main_async():
    # Get Telegram Channel ID
    if ARGS.get_telegram_updates:
        LOGGER.info('Getting telegram channel id...')
        print(get_telegram_updates()); exit()
    
    # Input Section
    ## Nextcloud Form Input
    if ARGS.update_ncform:
        update_ncform()
    
    # Server Section    
    ## Fetch Events from CalDav-Server
    data:list[Category] =  [Category(line) for line in CALENDARS]
    ## Create a Message in TXT, MD & HTML
    message: MultiFormatMessage = create_message(data)
        
    # Output Section
    ## UMap Output
    if ARGS.update_map: 
        LOGGER.info(f"Creating GeoJSON Data for the map...")
        create_mapdata(data)
    ## Print Output
    if ARGS.print: 
        LOGGER.info(f"Printing message in {FORMAT} Format: \n")
        print(message.get(FORMAT))
    ## Mail Output
    if ARGS.send_mail: 
        LOGGER.info('Sending Message per Mail...')
        send_mail(message)
    ## Send or Edit Telegram Message
    if ARGS.telegram:
        await send_or_edit_telegram(message)
    LOGGER.info('Finished all Tasks - Quitting.')
    exit()
    
# send mastodon newsletter #TODO Implement Mastodon
    # if ARGS.send_mastodon:
    #    mastodon = LOGin(config)
    #    print(mastodon.me())
    #    mastodon.toot(message(config, events, START, end, Format.MD)) 

# Run as Module or Standalone program
if __name__ in {"__main__", "__mp_main__"}:
    main()

    
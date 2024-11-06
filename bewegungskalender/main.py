# external imports
import asyncio
import locale
from locale import setlocale, LC_TIME

from bewegungskalender.classes.category import Category
# internal imports
from bewegungskalender.functions.cli import FORMAT, ARGS
from bewegungskalender.functions.logger import LOGGER
from bewegungskalender.functions.config import LOCALE
from bewegungskalender.functions.nextcloud_forms import update_ncform
from bewegungskalender.functions.calDAV import search_events
from bewegungskalender.classes.message import MultiFormatMessage, create_message
from bewegungskalender.output.telegram_bot import get_telegram_updates, send_or_edit_telegram
from bewegungskalender.output.map import create_mapdata
from bewegungskalender.output.mail import send_mail
from bewegungskalender.ui.main_page import start_ui

# Set locale
LOGGER.info(f"Args: {ARGS}")
LOGGER.debug('Setting locale...')
setlocale(locale.LC_ALL, LOCALE)

# Main Function if run as standalone program
def main():
    # ui.run can't be called from async call
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
    data:list[Category] = search_events()
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

    
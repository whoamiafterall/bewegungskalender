# external imports
import asyncio
from typing import NamedTuple
from locale import setlocale, LC_TIME

# internal imports
from bewegungskalender.helper.cli import LOGLEVEL, FORMAT, ARGS, START, END #set_telegram_channel
from bewegungskalender.helper.logger import LOG
from bewegungskalender.helper.config import CONFIG
from bewegungskalender.input.nextcloud_forms import update_ncform
from bewegungskalender.input.wpforms import update_wpform
from bewegungskalender.server.calDAV import connect_davclient, search_events
from bewegungskalender.output.message import MultiFormatMessage, create_message
from bewegungskalender.output.telegram_bot import send_or_edit_telegram # get_telegram_updates
from bewegungskalender.output.umap import createMapData
from bewegungskalender.output.mailnewsletter import send_mail
from bewegungskalender.ui.main_page import start_ui

# Set locale
LOG.info(f"Args: {ARGS}")
LOG.debug('Setting locale...')
setlocale(LC_TIME, CONFIG['format']['locale'])

# Main Function if run as standalone program
def main():
    # ui.run can't be called from async call
    if ARGS.user_interface: 
        LOG.info("Starting User Interface!")
        start_ui()
    else:
        asyncio.run(main_async())

# Main async function call if not running NiceGui
async def main_async():
    #FIXME get_telegram_updates
    # Telegram Config
    #if ARGS.get_telegram_updates: 
    #    LOG.info('Getting telegram channel id...')
    #    print(get_telegram_updates(config)); exit() 
    
    # Input Section
    ## WPForms Input
    input_calendar = connect_davclient(CONFIG).calendar(url=CONFIG['input']['calendar'])
    if ARGS.update_wpform:   
        update_wpform(CONFIG, input_calendar) 
    ## Nextcloud Form Input
    if ARGS.update_ncform != None:
        update_ncform(CONFIG['ncform']['url'], input_calendar)
    
    # Server Section    
    ## Fetch Events from CalDav-Server
    data:list[NamedTuple] = search_events(CONFIG, START, END, expand=True)
    ## Create a Message in TXT, MD & HTML
    message: MultiFormatMessage = create_message(CONFIG, data)
    #print(message.__str__)
        
    # Output Section
    ## UMap Output
    if ARGS.update_map: 
        LOG.info(f"Creating GeoJSON Data for the map...")
        createMapData(data, CONFIG['mapdatadir'], CONFIG['locationcatchdir'])
    ## Print Output
    if ARGS.print: 
        LOG.info(f"Printing message in {ARGS.format} Format: \n")
        print(message.get(ARGS.format))
    ## Mail Output
    if ARGS.send_mail: 
        LOG.info('Sending Message per Mail...')
        send_mail(CONFIG, message, START, END)
    ## Send or Edit Telegram Message
    if ARGS.telegram:
        channel = None #set_telegram_channel(ARGS.telegram, config)
        await send_or_edit_telegram(channel, CONFIG['datadir'], message, edit=ARGS.telegram_edit)
    LOG.info('Finished all Tasks - Quitting.')
    exit()
    
# send mastodon newsletter #TODO Implement Mastodon
    # if ARGS.send_mastodon:
    #    mastodon = LOGin(config)
    #    print(mastodon.me())
    #    mastodon.toot(message(config, events, START, end, Format.MD)) 

# Run as Module or Standalone program
if __name__ in {"__main__", "__mp_main__"}:
    main()

    
import asyncio
from typing import NamedTuple
from locale import setlocale, LC_TIME
from logging import debug, info
from bewegungskalender.helper.cli import args, start, stop, set_print_format, set_telegram_channel
from bewegungskalender.helper.config import config
from bewegungskalender.helper.datetime import set_timezone
from bewegungskalender.helper.formatting import Format
from bewegungskalender.input.nextcloud_forms import update_ncform
from bewegungskalender.input.wpforms import update_wpform
from bewegungskalender.server.calDAV import connect_davclient, search_events
from bewegungskalender.output.message import MultiFormatMessage, get_message
from bewegungskalender.output.telegram import send_or_edit_telegram, get_telegram_updates
from bewegungskalender.output.umap import createMapData
from bewegungskalender.output.mailnewsletter import send_mail
from bewegungskalender.ui.main_page import start_ui

# Set Timezone and locale
debug('Setting timezone and locale...')
setlocale(LC_TIME, config['format']['locale']) 
set_timezone(config)

# Main Function if run as standalone program
def main():
    # ui.run can't be called from async call
    if args.user_interface: 
        info("Starting User Interface!")
        start_ui()
    else:
        asyncio.run(main_async())

# Main Async Funktion call if not running NiceGui
async def main_async():
    # Telegram Config
    if args.get_telegram_updates: 
        info('Getting telegram channel id...')
    #    print(get_telegram_updates(config)); exit() 
    
    # Input Section
    ### WPForms Input
    input_calendar = connect_davclient(config).calendar(url=config['input']['calendar'])
    if args.update_wpform:   
        update_wpform(config, input_calendar) 
    ### Nextcloud Form Input
    if args.update_ncform != None:
        update_ncform(config['ncform']['url'], input_calendar)
    
    # Server Section    
    ### Fetch Events from CalDav-Server
    data:list[NamedTuple] = search_events(config, start, stop, expand=True)
    ### Create a Message in TXT, MD & HTML
    message: MultiFormatMessage = get_message(config, data, start, stop)
        
    # Output Section
    ### UMap Output
    if args.update_map: 
        info(f"Creating GeoJSON Data for the map...")
        createMapData(data, config['mapdatadir'], config['locationcatchdir'])
    ### Print Output
    if args.print: 
        info(f"Printing message in {args.print} Format: \n")
        print(set_print_format(args, message))
    ### Mail Output
    if args.send_mail: 
        info('Sending Message per Mail...')
        send_mail(config, message, start, stop)
    ### Send or Edit Telegram Message
    if args.telegram:
        channel = set_telegram_channel(args.telegram, config)
        await send_or_edit_telegram(channel, config['datadir'], message, edit=args.telegram_edit)
    info('Finished all Tasks - Quitting.')
    exit()
    
# send mastodon newsletter
    # if args.send_mastodon:
    #    mastodon = login(config)
    #    print(mastodon.me())
    #    mastodon.toot(message(config, events, start, end, Format.MD)) 

# Run as Module or Standalone program
if __name__ in {"__main__", "__mp_main__"}:
    main()

    
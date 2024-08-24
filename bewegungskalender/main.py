import asyncio
from typing import NamedTuple
import locale
import logging
from bewegungskalender.helper.cli import args, start, stop, set_print_format, set_telegram_channel
from bewegungskalender.helper.config import config
from bewegungskalender.helper.datetime import set_timezone
from bewegungskalender.helper.formatting import Format
from bewegungskalender.input.nextcloud_forms import update_ncform
from bewegungskalender.input.wpforms import update_wpform
from bewegungskalender.server.calDAV import connect_davclient, search_events
from bewegungskalender.output.message import get_message
from bewegungskalender.output.telegram import send_or_edit_telegram, get_telegram_updates
from bewegungskalender.output.umap import createMapData
from bewegungskalender.output.mailnewsletter import send_mail

# Main Function if run as standalone program
async def main():
    # Set Timezone and Locale
    logging.debug('Setting timezone and locale...')
    locale.setlocale(locale.LC_TIME, config['format']['locale']) 
    set_timezone(config)
    
    # Telegram Config
    if args.get_telegram_updates: 
        logging.info('Getting telegram channel id...')
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
    
    # Output Section
    ### UMap Output
    if args.update_map: 
        logging.info(f"Creating GeoJSON Data for the map...")
        createMapData(data, config['datadir'])
    ### Print Output
    if args.print: 
        logging.info(f"Printing message in {args.print} Format: \n")
        print(set_print_format(args, get_message(config, data, start, stop)))
    ### Mail Output
    if args.send_mail: 
        logging.info('Sending Message per Mail...')
        send_mail(config, start, stop, data, Format.HTML)
    ### Send or Edit Telegram Message
    if args.telegram:
        channel = set_telegram_channel(args.telegram, config)
        await send_or_edit_telegram(channel, config['datadir'], get_message(config, data, start, stop), edit=args.telegram_edit)
    logging.info('Finished all Tasks - Quitting.')
    exit()
    
# send mastodon newsletter
    # if args.send_mastodon:
    #    mastodon = login(config)
    #    print(mastodon.me())
    #    mastodon.toot(message(config, events, start, end, Format.MD)) 

# Run as Module or Standalone program
if __name__ == '__main__':
    asyncio.run(main())
    
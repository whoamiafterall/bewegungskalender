import asyncio
import datetime
from typing import NamedTuple
import yaml
import locale
import logging
from bewegungskalender.helper.cli import get_args, set_mail_recipients, set_print_format
from bewegungskalender.helper.datetime import set_timezone, today, days
from bewegungskalender.helper.formatting import Format
from bewegungskalender.input.wpforms import update_events
from bewegungskalender.server.calDAV import search_events
from bewegungskalender.output.message import message
from bewegungskalender.output.telegram import edit_telegram, send_telegram, get_telegram_updates
from bewegungskalender.output.umap import createMapData
from bewegungskalender.output.mailnewsletter import send_mail
#from bewegungskalender.output.mastodon import login

# Main Function if run as standalone program
async def main():
    # get Arguments from Command-Line and set log-level
    args:dict = get_args()
    if args.debug == True:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)
    logging.info(f"Args: {args}")
    
    # get Config from yml file
    logging.debug('Loading config file...')
    try:
        with open(args.config_file, 'r') as f: 
            config:dict = yaml.load(f, Loader=yaml.FullLoader) 
    except FileNotFoundError:
        logging.exception('Config File not Found:', args.config_file); exit()
        
    # Set Timezone and Locale
    logging.debug('Setting timezone and locale...')
    locale.setlocale(locale.LC_TIME, config['format']['locale']) 
    set_timezone(config)
    
    # Telegram Config
    if args.get_telegram_updates: 
        logging.info('Getting telegram channel id...')
        print(get_telegram_updates(config)); exit() 
    
    # Input Section
    ### WPForms Input
    if args.update_events:   
        update_events(config) 
    
    # Server Section    
    ### Fetch Events from CalDav-Server
    start:datetime.date = today() + days(args.query_start); 
    stop:datetime.date = start + days(args.query_end)
    data:list[NamedTuple] = search_events(config, start, stop, expand=True)
    
    # Output Section
    ### UMap Output
    if args.update_map: 
        localdir:str = config['umap']['localdir']
        remote:str = config['umap']['repo']
        logging.info(f"Creating GeoJSON Files in {localdir} and pushing them to {remote}...")
        createMapData(data, localdir, remote)
    ### Print Output
    if args.print: 
        logging.info(f"Printing message in {args.print} Format: \n")
        print(message(config, data, start, stop, set_print_format(args)))
    ### Mail Output
    if args.send_mail: 
        logging.info('Sending Message per Mail...')
        send_mail(config, start, stop, data, set_mail_recipients(args, config), Format.HTML)
    ### Send to Telegram
    if args.telegram: 
        logging.info('Sending Message to Telegram Channel...')
        await send_telegram(args, config, message(config, data, start, stop, Format.MD))
        logging.info(f"Succesfully sent message to Telegram Channel {args.telegram}!")
    ### Edit Telegram
    if args.edit_telegram: 
        logging.info('Editing last Message in Telegram Channel...')
        await edit_telegram(args, config, message(config, data, start, stop, Format.MD))
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
    
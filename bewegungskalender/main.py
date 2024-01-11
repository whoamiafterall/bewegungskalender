"""
main executable
"""
import argparse
import yaml
import locale
import logging
from bewegungskalender.helper.datetime import set_timezone, today, days
from bewegungskalender.helper.formatting import Format
from bewegungskalender.input.form import update_events
from bewegungskalender.nextcloud.fetch import fetch_events
from bewegungskalender.output.message import message
from bewegungskalender.output.telegram import send_telegram, get_telegram_updates
from bewegungskalender.output.umap import createMapData
from bewegungskalender.output.mail import send_mail
#from bewegungskalender.output.mastodon import login

# Get Arguments from Commandline 
def get_args ():
    argparser = argparse.ArgumentParser(description='Fetch CalDav Events from a Nextcloud and send a Message to Telegram.')
    argparser.add_argument("-c", "--config", dest='config_file', help='specify path to config file, defaults to config.yml')
    argparser.add_argument("-g", "--get-telegram-updates", dest='get_telegram_updates', help='get telegram id of channel', action='store_true')
    argparser.add_argument("-m", "--map", dest='update_map', help='create MapData in geojson from loaction entries of events', action='store_true')
    argparser.add_argument("-n", "--newsletter", dest='send_mail', help='send email-to recipients specified or from config', action='store_true')
    argparser.add_argument("-p", "--print", dest='print', help='print message to stdout and select format from html, markdown or plain-text - for debugging', choices=['html','md','txt'], action='store')
    argparser.add_argument("-qs", "--query-start", dest='query_start', type=int, help='starting day to query events from CalDav server, 0/None means today')
    argparser.add_argument("-qe", "--query-end", dest='query_end', type=int, help='number of days to query events from CalDav server, starting from query-start')
    argparser.add_argument("-r", "--recipients", dest='recipient', help='override mail recipients from config')
    argparser.add_argument("-t", "--telegram", dest='telegram', help='send message to telegram - choose production or test_channel specified in config', choices=['prod', 'test'])
    argparser.add_argument("-toot", "--mastodon", dest='send_mastodon', help='send toot to mastodon', action='store_true')
    argparser.add_argument("-u", "--update-events", dest='update_events', help='check Mailbox for new events and add them to calendar', action='store_true')
    argparser.set_defaults(config_file="config.yml", print=None, query_start=1, query_end=1, telegram=None)
    args = argparser.parse_args()
    return args

# Main Function if run as standalone program
def main(events = {}):
    logging.basicConfig(level=logging.DEBUG)
    logging.debug('Started bewegungskalender.main...')
    logging.debug('Parsing arguments from command-line...')
    args = get_args() # get Arguments from Command-Line
    try: # get Config Dictionary from YAML file
        with open(args.config_file, 'r') as f: 
            logging.debug('Loading config file...')
            config:dict = yaml.load(f, Loader=yaml.FullLoader) 
    except FileNotFoundError:
        logging.error('Config File not Found.', args.config_file, FileNotFoundError); exit()
    logging.debug('Setting timezone and locale...')
    locale.setlocale(locale.LC_TIME, config['format']['locale']) 
    set_timezone(config)
    if args.get_telegram_updates: 
        #get id of telegram channel where the bot has been added
        logging.debug('Getting telegram channel id...')
        print(get_telegram_updates(config)); exit() 
    if args.update_events: 
        #update events from Form Mails sent by WP Forms Lite
        logging.debug('Updating Events by scanning E-Mails...')
        update_events(config)    
    #Search nextcloud calendars for events in a specific range
    start = today() + days(args.query_start); 
    end = start + days(args.query_end) 
    logging.debug('Fetching Events from Nextcloud server...')
    events = fetch_events(config, start, end)
    if args.update_map: 
        #create GeoJSON Files
        logging.debug('Creating Map Data and writing to GeoJSON Files...')
        createMapData(events)
    if args.print: 
        #print message to stdout for debugging or copying
        logging.debug('Printing Message to stdout...')
        print(f"This is the message in {args.print} Format: \n")
        #set Format to cli-argument (HTML, MarkDown or TXT)
        if args.print == 'html':
            format = Format.HTML     
        elif args.print == 'md':
            format = Format.MD
        else:
            format = Format.TXT
        print(message(config, events, start, end, format))
    if args.send_mail: 
        #send message as mail newsletter
        logging.debug('Sending Message per Mail...')
        #set recipients to cli-arguments or config
        if args.recipient is not None:
            recipients = args.recipient 
        else: 
            config['mail']['newsletter']['recipients']
        send_mail(config, start, end, events, recipients, Format.HTML)
    if args.telegram: 
        #send message to telegram 
        logging.debug('Sending Message to Telegram Channel...')
        #set telegram channel to production or test
        if args.telegram == 'prod':
            channel = config['telegram']['production'] 
        else:
            config['telegram']['test']
        text = message(config, events, start, end, Format.MD) 
        send_telegram(config, channel, text)
        print(f"Succesfully sent message to {args.telegram}: {channel}!")
    logging.debug('Finished all Tasks - Quitting.')
    exit()
    
# send mastodon newsletter
    # if args.send_mastodon:
    #    mastodon = login(config)
    #    print(mastodon.me())
    #    mastodon.toot(message(config, events, start, end, Format.MD)) 

# Run as Module or Standalone program
if __name__ == '__main__':
    output = main()
    if output:
        print(output, end='')
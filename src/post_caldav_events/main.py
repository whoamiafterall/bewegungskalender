"""
main executable
"""
import argparse
import yaml
import locale
from post_caldav_events.helper.datetime import set_timezone, today, days
from post_caldav_events.helper.formatting import Format
from post_caldav_events.input.form import update_events
from post_caldav_events.nextcloud.fetch import fetch_events
from post_caldav_events.output.message import message
from post_caldav_events.output.telegram import send_telegram, get_telegram_updates
from post_caldav_events.output.umap import createMapData
from post_caldav_events.output.newsletter import send_newsletter
from post_caldav_events.output.mastodon import login

# Get Arguments from Commandline 
def get_args ():
    argparser = argparse.ArgumentParser(description='Fetch CalDav Events from a Nextcloud and send a Message to Telegram.')
    argparser.add_argument("-c", "--config", dest='config_file', help='specify path to config file, defaults to config.yml')
    argparser.add_argument("-g", "--get-telegram-updates", dest='get_telegram_updates', help='get telegram id of channel', action='store_true')
    argparser.add_argument("-m", "--map", dest='update_map', help='create MapData in geojson from loaction entries of events', action='store_true')
    argparser.add_argument("-n", "--newsletter", dest='send_newsletter', help='send email-newsletter', action='store_true')
    argparser.add_argument("-p", "--print", dest='print', help='print message to stdout and select format from html, markdown or plain-text - for debugging', choices=['html','md','txt'], action='store')
    argparser.add_argument("-qs", "--query-start", dest='query_start', type=int, help='starting day to query events from CalDav server, 0/None means today')
    argparser.add_argument("-qe", "--query-end", dest='query_end', type=int, help='number of days to query events from CalDav server, starting from query-start')
    argparser.add_argument("-r", "--recipients", dest='recipient', help='override newsletter recipients from config - useful for testing')
    argparser.add_argument("-t", "--telegram", dest='send_telegram', help='send message to telegram - choose production or test_channel specified in config', choices=['prod', 'test'])
    argparser.add_argument("-toot", "--mastodon", dest='send_mastodon', help='send toot to mastodon', action='store_true')
    argparser.add_argument("-u", "--update-events", dest='update_events', help='check Mailbox for new events and add them to calendar', action='store_true')
    argparser.set_defaults(config_file="config.yml", print=None, query_start=1, query_end=1, telegram='prod')
    args = argparser.parse_args()
    return args

# Main Function if run as standalone program
def main(events = {}):
    
# get Arguments from CLI
    args = get_args() 
    
# get Config from YAML file
    try: 
        with open(args.config_file, 'r') as f:
            config = yaml.load(f, Loader=yaml.FullLoader)
    except FileNotFoundError:
        print("Config File not Found"); exit() 
        
# set time and language locale, timezone and message format
    locale.setlocale(locale.LC_TIME, config['format']['locale'])
    set_timezone(config)
    
# get id from telegram group/channel
    if args.get_telegram_updates: 
        print(get_telegram_updates(config)); exit()
        
# update events from Form Mails    
    if args.update_events:
        update_events(config)
        
# create datetime objects for the query start and end with args from cli
    querystart = today() + days(args.query_start) 
    queryend = querystart + days(args.query_end) 
    
# get events from nextcloud
    events = fetch_events(config, querystart, queryend) 
    
# update the umap 
    if args.update_map:
        createMapData(events) 
        
# print message to stdout
    if args.print is not None:
        print(args.print)
        format = Format.HTML if args.print == 'html' else (Format.MD if args.print == 'md' else Format.TXT)
        print(message(config, events, querystart, queryend, format))
        
# send mail newsletter
    if args.send_newsletter:
        recipientcli = args.recipient if args.recipient is not None else None
        send_newsletter(config, querystart, queryend, events, recipientcli, Format.HTML) 
        
# send telegram 
    channel = config['telegram']['test_channel'] if args.telegram is 'test' else config['telegram']['prod_channel']  
    send_telegram(config, channel, message(config, events, querystart, queryend, Format.MD)) 
        
# send mastodon newsletter
    if args.send_mastodon:
        mastodon = login(config)
        print(mastodon.me())
        mastodon.toot(message(config, events, querystart, queryend, Format.MD)) 
    exit()

# Run as Module or Standalone program
if __name__ == '__main__':
    output = main()
    if output:
        print(output, end='')
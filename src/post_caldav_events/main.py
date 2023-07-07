"""
main executable
"""
import argparse
import yaml
import datetime
from post_caldav_events.input.form import update_events
from post_caldav_events.nextcloud.fetch import fetch_events, set_locale, set_timezone
from post_caldav_events.output.message import message
from post_caldav_events.output.telegram import send_telegram, get_telegram_updates
from post_caldav_events.output.umap import createMapData

# Get Arguments from Commandline 
def get_args (override_args = None):
    argparser = argparse.ArgumentParser(description='Fetch CalDav Events from a Nextcloud and send a Message to Telegram.')
    argparser.add_argument("-c", "--config", dest='config_file', help='path to config file')
    argparser.add_argument("-qs", "--query-start", dest='query_start', type=int, help='starting day to query events from CalDav server, 0 means today')
    argparser.add_argument("-qe", "--query-end", dest='query_end', type=int, help='number of days to query events from CalDav server, starting from query-start')
    argparser.add_argument("-g", "--get-telegram-updates", dest='get_telegram_updates', help='get telegram id of channel', action='store_true')
    argparser.add_argument("-u", "--update-events", dest='update_events', help='check Mailbox for new events and add them to calendar', action='store_true')
    argparser.add_argument("-m", "--map", dest='update_map', help='create MapData in geojson from loaction entries of events', action='store_true')
    argparser.add_argument("-t", "--telegram", dest='send_telegram', help='send message to telegram', action='store_true')
    argparser.set_defaults(config_file="config.yml", query_start=1, query_end=1)
    if override_args is None:
        args = argparser.parse_args()
    else:
        args = argparser.parse_args(override_args)
    return args

# Get Config from Config File
def get_config(args, config = {}):
    try:
        with open(args.config_file, 'r') as f:
            config = yaml.load(f, Loader=yaml.FullLoader)
    except FileNotFoundError:
        print("Config File not Found")
    return config

    return 

# Main Function if run as standalone program
def main(events = {}):
    args = get_args()
    print(args)
    config = get_config(args)
    if args.get_telegram_updates:
        print(get_telegram_updates())
        exit()
    if args.update_events:
        update_events(config)
    set_timezone(config)
    set_locale(config)
    querystart = datetime.datetime.now().date() + datetime.timedelta(days=args.query_start)
    queryend = querystart + datetime.timedelta(days=args.query_end)
    events = fetch_events(config, querystart, queryend)
    if args.update_map:
        createMapData(events)
    if args.send_telegram:
        send_telegram(config, message(events, querystart, queryend, markdown=True))
    exit()

# Run as Module or Standalone program
if __name__ == '__main__':
    output = main()
    if output:
        print(output, end='')
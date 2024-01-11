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
from post_caldav_events.output.mail import send_mail
#from post_caldav_events.output.mastodon import login

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
    args = get_args() # get Arguments from Command-Line
    try: 
        with open(args.config_file, 'r') as f: 
            config:dict = yaml.load(f, Loader=yaml.FullLoader) # get Config Dictionary from YAML file
    except FileNotFoundError:
        print("Config File not Found"); exit()
    locale.setlocale(locale.LC_TIME, config['format']['locale']) # set time and language locale by config
    set_timezone(config) #set timezone by config
    if args.get_telegram_updates: 
        print(get_telegram_updates(config)); exit() # get id from telegram group/channel 
    if args.update_events:
        update_events(config) # update events from Form Mails sent by WP Forms Lite (a Wordpress Plugin)
    querystart = today() + days(args.query_start); queryend = querystart + days(args.query_end) # create datetime objects for the query start and end with args from cli
    events = fetch_events(config, querystart, queryend) #fetch events from nextcloud caldav server
    if args.update_map: # 
        createMapData(events) # update the geojson data files
    if args.print: # for debugging
        print(f"This is the message in {args.print} Format: \n") # print Format for debugging
        format = Format.HTML if args.print == 'html' else (Format.MD if args.print == 'md' else Format.TXT) # set Format to cli-argument specified
        print(message(config, events, querystart, queryend, format)) # print message to stdout in the format specified above
    if args.send_mail: # mail newsletter
        recipientcli = args.recipient if args.recipient is not None else None # get mail recipients from config or from cli-argument
        send_mail(config, querystart, queryend, events, recipientcli, Format.HTML) # send message as mail newsletter
    if args.telegram: # telegram newsletter
        channel = config['telegram']['production'] if args.telegram == 'prod' else config['telegram']['test']  #set telegram channel to production or test
        send_telegram(config, channel, message(config, events, querystart, queryend, Format.MD)) # send message to telegram channel
        print(f"Succesfully sent message to {args.telegram}: {channel}!") # print channel id for debugging
    exit() # end script
# send mastodon newsletter
    # if args.send_mastodon:
    #    mastodon = login(config)
    #    print(mastodon.me())
    #    mastodon.toot(message(config, events, querystart, queryend, Format.MD)) 

# Run as Module or Standalone program
if __name__ == '__main__':
    output = main()
    if output:
        print(output, end='')
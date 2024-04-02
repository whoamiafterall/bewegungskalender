import argparse
import sys
from bewegungskalender.helper.formatting import Format

# Get Arguments from Commandline 
def get_args ():
    # Get Argparser and add arguments
    argparser = argparse.ArgumentParser(prog="bewegungskalender", description='Use a CalDAV-Server to send automatic calendar newsletters to the world.')
    argparser.add_argument("-c", "--config", dest='config_file', help='specify path to config file, defaults to config.yml')
    argparser.add_argument("-d", "--debug", dest='debug', help='set the log level to debug, defaults to info', action='store_true')
    argparser.add_argument("-g", "--get-telegram-updates", dest='get_telegram_updates', help='get telegram id of channel', action='store_true')
    argparser.add_argument("-m", "--map", dest='update_map', help='create MapData in geojson from loaction entries of events', action='store_true')
    argparser.add_argument("-n", "--newsletter", dest='send_mail', help='send email-to recipients specified or from config', action='store_true')
    argparser.add_argument("-p", "--print", dest='print', help='print message to stdout and select format from html, markdown or plain-text - defaults to txt', choices=['html','md','txt'], action='store')
    argparser.add_argument("-qs", "--query-start", dest='query_start', type=int, help='starting day to query events from CalDav server, 0 means today, 1 tomorrow - defaults to 1')
    argparser.add_argument("-qe", "--query-end", dest='query_end', type=int, help='range of days to query events from CalDav server, starting from query-start - defaults to 14')
    argparser.add_argument("-r", "--recipients", dest='recipient', help='override mail recipients from config')
    argparser.add_argument("-t", "--telegram", dest='telegram', help='send message to telegram - choose production or test_channel specified in config - defaults to test', choices=['prod', 'test'])
    argparser.add_argument("-toot", "--mastodon", dest='send_mastodon', help='send toot to mastodon', action='store_true')
    argparser.add_argument("-u", "--update-events", dest='update_events', help='check Mailbox for new events and add them to calendar', action='store_true')
    argparser.set_defaults(config_file="config.yml", log_level='info', query_start=1, query_end=14)
    # Show help if no argument specified
    if len(sys.argv) <= 1:
        sys.argv.append('--help')
    args = argparser.parse_args()
    return args

# Handle --print and set Format to HTML, MarkDown or TXT
def set_print_format(args):
    if args.print == 'html':
        format = Format.HTML     
    elif args.print == 'md':
        format = Format.MD
    else:
        format = Format.TXT
    return format

#  Handle --telegram and set channel to production if specified
def set_telegram_channel(args, config):
    if args.telegram == 'prod':
        channel = config['telegram']['production'] 
    else:
        channel = config['telegram']['test']
    return channel

 # Handle --recipients and set recipients if specified
def set_mail_recipients(args, config):
    if args.recipient is not None:
        return args.recipient 
    else: 
        return config['newsletter']['recipients']
import argparse
from datetime import date, timedelta
from logging import exception
import logging
import sys
from bewegungskalender.output.message import MultiFormatMessage
from bewegungskalender.output.telegram import Channel

# Get Arguments from Commandline 
def get_args() -> dict:
    # Get p and add arguments
    p = argparse.ArgumentParser(prog="bewegungskalender", description='Use a CalDAV-Server to send automatic calendar newsletters to the world.')
    p.add_argument("-c", "--config", dest='config_file', help='specify path to config file, defaults to config.yml')
    p.add_argument("-d", "--debug", dest='debug', help='set the log level to debug, defaults to info', action='store_true')
    p.add_argument("-g", "--get-telegram-updates", dest='get_telegram_updates', help='get telegram id of channel', action='store_true')
    p.add_argument("-m", "--map", dest='update_map', help='create MapData in geojson from loaction entries of events', action='store_true')
    p.add_argument("-n", "--newsletter", dest='send_mail', help='send email-to recipients specified or from config', action='store_true')
    p.add_argument("-nc", "--update-ncform", dest='update_ncform', type=int, help='get new events in the last X days submitted to Nextcloud Form')
    p.add_argument("-p", "--print", dest='print', help='print message to stdout and select format from html, markdown or plain-text - defaults to txt', choices=['html','md','txt'], action='store')
    p.add_argument("-qs", "--query-start", dest='query_start', type=int, help='starting day to query events from CalDav server, 0 means today, 1 tomorrow - defaults to 1')
    p.add_argument("-qe", "--query-end", dest='query_end', type=int, help='range of days to query events from CalDav server, starting from query-start - defaults to 14')
    p.add_argument("-r", "--recipients", dest='recipient', help='override mail recipients from config')
    p.add_argument("-t", "--telegram", dest='telegram', help='send message to telegram - choose production or test_channel specified in config', choices=['prod', 'test'])
    p.add_argument("--edit", dest='telegram_edit', required='--telegram' in sys.argv, help='edit last telegram message instead of sending a new one', action='store_true')
    p.add_argument("-toot", "--mastodon", dest='send_mastodon', help='send toot to mastodon', action='store_true')
    p.add_argument("-wp", "--update-wpform", dest='update_wpform', help='check Mailbox for new events from WPForms and add them to calendar', action='store_true')
    p.set_defaults(config_file="config.yml", log_level='info', query_start=1, query_end=14)
    # Show help if no argument specified
    if len(sys.argv) <= 1:
        sys.argv.append('--help')
    args:dict = p.parse_args()
    return args

def set_log_level(args:dict):
    if args.debug == True:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)
    logging.info(f"Args: {args}")

# Handle --print and set Format to HTML, MarkDown or TXT
def set_print_format(args:dict, message:MultiFormatMessage) -> str:
    if args.print == 'html':
        return message.html     
    elif args.print == 'md':
        return message.markdown
    else:
        return message.txt
    
# Handle --telegram and set telegram Channel
def set_telegram_channel(type:str, config:dict) -> Channel:
    botToken = config['telegram']['token']
    if type == 'prod':
        return Channel(config['telegram']['production'], botToken, 'prod')
    if type == 'test':
        return Channel(config['telegram']['test'], botToken, 'test')

 # Handle --recipients and set recipients if specified
def set_mail_receiver(args:dict) -> list[str]:
    if args.recipient is not None:
        return list(args.recipient) 
    else:
        return None

# These are run when this module is imported
args = get_args()
set_log_level(args)
mail_receiver = set_mail_receiver(args)
# TODO add set_telegram_channel & set_print_format
start:date = date.today() + timedelta(args.query_start)
stop:date = start + timedelta(args.query_end)
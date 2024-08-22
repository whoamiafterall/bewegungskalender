import argparse
from logging import exception
import sys
from bewegungskalender.helper.formatting import Format
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
    p.add_argument("-p", "--print", dest='print', help='print message to stdout and select format from html, markdown or plain-text - defaults to txt', choices=['html','md','txt'], action='store')
    p.add_argument("-qs", "--query-start", dest='query_start', type=int, help='starting day to query events from CalDav server, 0 means today, 1 tomorrow - defaults to 1')
    p.add_argument("-qe", "--query-end", dest='query_end', type=int, help='range of days to query events from CalDav server, starting from query-start - defaults to 14')
    p.add_argument("-r", "--recipients", dest='recipient', help='override mail recipients from config')
    p.add_argument("-t", "--telegram", dest='telegram', help='send message to telegram - choose production or test_channel specified in config', choices=['prod', 'test'])
    p.add_argument("--mode", dest='telegram_mode', required='--telegram' in sys.argv, help='choose wether to edit last telegram message or send a new one', choices=['send', 'edit'])
    p.add_argument("-toot", "--mastodon", dest='send_mastodon', help='send toot to mastodon', action='store_true')
    p.add_argument("-u", "--update-events", dest='update_events', help='check Mailbox for new events and add them to calendar', action='store_true')
    p.set_defaults(config_file="config.yml", log_level='info', query_start=1, query_end=14, telegram_mode='send')
    # Show help if no argument specified
    if len(sys.argv) <= 1:
        sys.argv.append('--help')
    args:dict = p.parse_args()
    return args

# Handle --print and set Format to HTML, MarkDown or TXT
def set_print_format(args:dict, message:MultiFormatMessage) -> Format:
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
def set_mail_recipients(args:dict, config:dict) -> list[str]:
    if args.recipient is not None:
        return list(args.recipient) 
    else: 
        return config['newsletter']['recipients']
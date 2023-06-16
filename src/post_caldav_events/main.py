"""
main executable
"""
import argparse
import yaml
from post_caldav_events.utils import fetch_events, set_locale, set_timezone
from post_caldav_events.create import message
from post_caldav_events.types.telegram import send, get_updates
# from .types.mail import *

# Get Arguments from Commandline 
def get_args (override_args = None):
    argparser = argparse.ArgumentParser(description='Fetch CalDav Events from a Nextcloud and send a Message to Telegram.')
    argparser.add_argument("-c", "--config", dest='config_file', help='path to config file')
    argparser.add_argument("-g", "--get-telegram-updates", dest='get_telegram_updates', help='get telegram updates instead of sending message', action='store_true')
 #   argparser.add_argument("-d", "--debug", dest='debug_mode', help='print base message with iCalendar Component Data to debug', action='store_true')
    argparser.set_defaults(config_file="config.yml", get_telegram_updates=False, debug=False)
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
    
# send Telegram message from tgmarkdown.py
def tgmarkdown(config:dict):
    if config['output']['type'] == 'telegram':
        return
    else:
        print("No config found for Telegram. Please review your config file.")
        return

# send Mail from mail.py
def mail(config:dict):
    # TODO
    return

# Main Function if run as standalone program
def main(events = {}):
    args = get_args()
    config = get_config(args)
    if args.get_telegram_updates:
        print(get_updates())
    set_timezone(config)
    set_locale(config)
    events = fetch_events(config)
    send(config, message(events, config, True))
    exit()

# Run as Module or Standalone program
if __name__ == '__main__':
    output = main()
    if output:
        print(output, end='')
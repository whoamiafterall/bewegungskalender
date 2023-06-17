"""
main executable
"""
import argparse
import yaml
from post_caldav_events.input.form import update_events
from post_caldav_events.nextcloud.fetch import fetch_events, set_locale, set_timezone
from post_caldav_events.output.message import message
from post_caldav_events.output.telegram import send, get_updates

# Get Arguments from Commandline 
def get_args (override_args = None):
    argparser = argparse.ArgumentParser(description='Fetch CalDav Events from a Nextcloud and send a Message to Telegram.')
    argparser.add_argument("-c", "--config", dest='config_file', help='path to config file')
    argparser.add_argument("-g", "--get-telegram-updates", dest='get_telegram_updates', help='get telegram updates instead of sending message', action='store_true')
    #argparser.add_argument("-u", "--update-events", dest='update_events', type=bool, help='check mailbox for new events and add them to calendar')
    argparser.set_defaults(config_file="config.yml", get_telegram_updates=False, debug=False, update_events=False)
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

# Main Function if run as standalone program
def main(events = {}):
    update = False
    args = get_args()
    config = get_config(args)
    if args.get_telegram_updates:
        print(get_updates())
    update_events(config)
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
import sys
from argparse import ArgumentParser, Namespace
from datetime import date, timedelta
from typing import Final
#from bewegungskalender.output.telegram import Channel

def get_ARGS() -> Namespace:
    """Creates an instance of Class **ArgumentParser** from **argparse** module which is used for parsing **command-line arguments**. <br>
    Configures the name and description of the program, aswell as several arguments and default values. <br>
    If **no argument** is specified it will display the **help view (--help/-h)**. <br>
    Returns the values of the arguments parsed from the command-line as a **dictionary**.

    Returns:
        dict: The **values** passed as command-line arguments as a **dictionary**, including **default values**.
    """    
    # Get parser
    cli = ArgumentParser(prog="bewegungskalender", description='Use a CalDAV-Server to send automatic calendar newsletters to the world.')
    # Add Arguments
    cli.add_argument("-c", "--config", dest='config_file', type=str, help='specify path to config file, defaults to config.yml', action='store', nargs='?')
    cli.add_argument("-l", "--loglevel", dest='loglevel', type=str, help='set the log level, defaults to info', choices=['debug', 'error'], action='store', nargs='?')
    cli.add_argument("-g", "--get-telegram-updates", dest='get_telegram_updates', help='get telegram id of channel', action='store_true')
    cli.add_argument("-m", "--map", dest='update_map', help='create MapData in geojson from loaction entries of events', action='store_true')
    cli.add_argument("-n", "--newsletter", dest='send_mail', help='send email-to recipients specified or from config', action='store_true')
    cli.add_argument("-to", dest='mail_to', required='send_mail' in sys.argv, type=str, action='store',
                      help='override mail receiver from config - only accepts one string as mail address')
    cli.add_argument("-nc", "--nextcloud", dest='update_ncform', action='store_true',
                        help='Get new events submitted to Nextcloud Form - use --since to specify a time range - defaults to 1 day.')
    cli.add_argument("--since", dest='last_update', required='--update_ncform' in sys.argv, type=int, action='store', nargs='?',
                        help='Specify how many days in the past you want to consider - defaults to 1 - depends on your cron interval', )
    
    cli.add_argument("-p", "--print", dest='print', required='--format' in sys.argv, help='print message to stdout - specify format with --format - defaults to plain-text', action='store_true')
    cli.add_argument("--format", dest='format', required='--print' in sys.argv, type=str, choices=['html','md','txt'], action='store', nargs='?',
                     help='choose format from html, markdown or plain-txt - defaults to txt')
    cli.add_argument("-qs", "--query-start", dest='query_start', type=int, help='starting day to query events from CalDav server, 0 means today, 1 tomorrow - defaults to 1')
    cli.add_argument("-qe", "--query-end", dest='query_end', type=int, help='range of days to query events from CalDav server, starting from query-start - defaults to 14')
    cli.add_argument("-t", "--telegram", dest='telegram', type=str, help='send message to telegram - choose production or test_channel specified in config', choices=['prod', 'test'], action='store')
    cli.add_argument("--edit", dest='telegram_edit', required='--telegram' in sys.argv, help='edit last telegram message instead of sending a new one', action='store_true')
    cli.add_argument("-toot", "--mastodon", dest='send_mastodon', help='send toot to mastodon', action='store_true')
    cli.add_argument("-ui", "--user-interface", dest='user_interface', help='start the user interface', action='store_true')
    cli.add_argument("-wp", "--update-wpform", dest='update_wpform', help='check Mailbox for new events from WPForms and add them to calendar', action='store_true')
    cli.set_defaults(config_file="config.yml", loglevel='info', format='txt', last_update=1, query_start=1, query_end=14)
    # Show help if no argument specified
    if len(sys.argv) <= 1:
        sys.argv.append('--help')
    return cli.parse_args()
        
# Handle --telegram and set telegram Channel
#def set_telegram_channel(type:str, config:dict) -> Channel:
#    botToken = config['telegram']['token']
#    if type == 'prod':
#        return Channel(config['telegram']['production'], botToken, 'prod')
#    if type == 'test':
#     return Channel(config['telegram']['test'], botToken, 'test')

# These are run when this module is imported
ARGS: Final[dict] = get_ARGS()
CONFIG_FILE: Final[str] = ARGS.config_file
START: Final[date] = date.today() + timedelta(ARGS.query_start)
END: Final[date] = START + timedelta(ARGS.query_end)
LOGLEVEL: Final[str] = ARGS.loglevel
LAST_UPDATE: Final[int] = ARGS.last_update # Specifies how many days in the past the Nextcloud Form events shall be considered
FORMAT: Final[str] = ARGS.format 
MAIL_TO: Final[str] = ARGS.mail_to
# TELEGRAM_CHANNEL: Final[Channel] = 
# TODO add set_telegram_channel 



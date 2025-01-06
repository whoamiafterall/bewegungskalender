import sys
from argparse import ArgumentParser, Namespace
from _datetime import timedelta, datetime
from typing import Final
#from bewegungskalender.output.telegram import Channel

def get_args() -> Namespace:
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

    cli.add_argument("-cr", "--credentials", dest='credentials_file', type=str, help='specify path to credentials file, defaults to credentials.yml', action='store', nargs='?')
    cli.add_argument("-db", "--database", dest='db_mode', help='Choose between full (Creates a new database and syncs from Nextcloud), sync (Syncs the existing database with Nextcloud), search (searches in a given time range using -qs and -qe)', action='store', choices=['full', 'sync', 'search'], nargs='?')
    cli.add_argument("-dump", "--dump-database", dest='db_dump',
                     help='Dump the Database for debugging. Choose between search and sync db.',
                     action='store', choices=['sync', 'search'], nargs='?')
    cli.add_argument("-g", "--get-telegram-updates", dest='get_telegram_updates', help='get telegram id of channel', action='store_true')
    cli.add_argument("-l", "--loglevel", dest='loglevel', type=str, help='set the log level, defaults to info', choices=['debug', 'error'], action='store', nargs='?')
   # cli.add_argument("-m", "--leaflet", dest='update_map', help='create MapData in geojson from loaction entries of events', action='store_true')
    cli.add_argument("-n", "--newsletter", dest='send_mail', help='send email-to recipients specified or from config', action='store_true')
    cli.add_argument("-to", dest='mail_to', required='send_mail' in sys.argv, type=str, action='store',
                      help='override mail receiver from config - only accepts one string as mail address')
    cli.add_argument("-nc", "--nextcloud", dest='update_ncform', action='store_true',
                        help='Get new events submitted to Nextcloud Form - use --since to specify a time range - defaults to 1 day.')
    cli.add_argument("--since", dest='last_update', required='--update_ncform' in sys.argv, type=int, action='store', nargs='?',
                        help='Specify how many days in the past you want to consider - defaults to 1 - depends on your cron interval', )
    
    cli.add_argument("-p", "--print", dest='print', help='print message to stdout - choose (html | md | txt)', action='store', choices=['html','md','txt'], nargs='?')
    cli.add_argument("-qs", "--query-start", dest='query_start', type=int, help='starting day to query events from CalDav server, 0 means today, 1 tomorrow - defaults to 1')
    cli.add_argument("-qe", "--query-end", dest='query_end', type=int, help='range of days to query events from CalDav server, starting from query-start - defaults to 14')
    cli.add_argument("-t", "--telegram", dest='telegram', type=str, help='send message to telegram - choose production or test_channel specified in config', choices=['prod', 'test'], action='store')
    cli.add_argument("--edit", dest='telegram_edit', required='--telegram' in sys.argv, help='edit last telegram message instead of sending a new one', action='store_true')
    cli.add_argument("-toot", "--mastodon", dest='send_mastodon', help='send toot to mastodon', action='store_true')
    cli.add_argument("-ui", "--user-interface", dest='user_interface', help='start the user interface', action='store_true')
    cli.set_defaults(config_file="config.yml", credentials_file="credentials.yml", dbmode=None ,loglevel='info', last_update=1, query_start=0, query_end=14)
    # Show help if no argument specified
    if len(sys.argv) <= 1:
        sys.argv.append('--help')
    return cli.parse_args()

# These are run when this module is imported
ARGS: Final[Namespace] = get_args()
CONFIG_FILE: Final[str] = ARGS.config_file
CREDENTIALS_FILE: Final[str] = ARGS.credentials_file
DB_MODE: Final[str] = ARGS.db_mode
DB_DUMP: Final[str] = ARGS.db_dump
START: Final[datetime] = datetime.now() + timedelta(ARGS.query_start)
END: Final[datetime] = START + timedelta(ARGS.query_end)
LOGLEVEL: Final[str] = ARGS.loglevel
LAST_UPDATE: Final[int] = ARGS.last_update # Specifies how many days in the past the Nextcloud Form events shall be considered
FORMAT: Final[str] = ARGS.print
MAIL_TO: Final[str] = ARGS.mail_to
TELEGRAM_CHANNEL: Final[str] = ARGS.telegram
TELEGRAM_EDIT: Final[bool] = ARGS.telegram_edit

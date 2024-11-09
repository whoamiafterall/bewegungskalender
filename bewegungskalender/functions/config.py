from typing import Final

import pytz
import yaml
from docutils.nodes import strong
from pytz.tzinfo import StaticTzInfo

from bewegungskalender.functions.cli import CONFIG_FILE
from bewegungskalender.functions.logger import LOGGER

# get Config from yml file
LOGGER.debug('Loading config file...')
try:
    with open(CONFIG_FILE, 'r') as f: 
        CONFIG:dict = yaml.load(f, Loader=yaml.FullLoader)
except FileNotFoundError:
    LOGGER.exception('Config File not Found:', CONFIG_FILE); exit()

# Mail Section
MAIL_SRV: Final[str] = CONFIG['mail']['server']
SMTP: Final[int] = CONFIG['mail']['smtp_port']
MAIL_ACC: Final[str] = CONFIG['mail']['account']
MAIL_PW: Final[str] = CONFIG['mail']['password']
MAIL_SUBJECT: Final[str] = CONFIG['mail']['subject']
MAIL_SENDER: Final[str] = CONFIG['mail']['sender']
MAIL_RECEIVER: Final[list] = CONFIG['mail']['receiver']

# Data-Section
MAPDATA_CACHE: Final[str] = CONFIG['mapdata_dir']
LOCATION_CACHE: Final[str] = CONFIG['location_cache_dir']
DATADIR: Final[str] = CONFIG['datadir']
TEMPLATING_DIR: Final[str] = CONFIG['templating_dir']

# UI-Section
UI_PORT: Final[int] = CONFIG['ui']['port']
UI_TITLE: Final[str] = CONFIG['ui']['title']
UI_FAVICON: Final[str] = CONFIG['ui']['favicon']
MAIN_MENU: Final[dict[str, dict]] = CONFIG['main_menu']
SECONDARY_MENU: Final[dict[str,dict]] = CONFIG['secondary_menu']

# Map-Section
MAP_ZOOM: Final[int] = CONFIG['map']['zoom']
MAP_CENTER_LAT: Final[float] = CONFIG['map']['center_lat']
MAP_CENTER_LON: Final[float] = CONFIG['map']['center_lon']
MAP_POPUP_TEMPLATE: Final[str] = CONFIG['map']['popup-template']

# Input-Section
INPUT_CALENDAR: Final[str] = CONFIG['input_calendar']
NCFORM_URL: Final[str] = CONFIG['ncform']['url']

# Telegram-Section
TELEGRAM_TOKEN: Final[str] = CONFIG['telegram']['token']
TELEGRAM_PRODUCTION: Final[str] = CONFIG['telegram']['production']
TELEGRAM_TEST: Final[str] = CONFIG['telegram']['test_channel']

# CalDav-Section
CALENDARS: Final[list[dict]] = CONFIG['calendars']
CALDAV_URL: Final[str] = CONFIG['caldav']['url']
CALDAV_USR: Final[str] = CONFIG['caldav']['username']
CALDAV_PW: Final[str] = CONFIG['caldav']['password']

# Format-Section
FOOTER: Final[list[dict]] = CONFIG['footer']
LOCALE: Final[str] = CONFIG['format']['locale']
TIMEZONE: Final[StaticTzInfo] = pytz.timezone(CONFIG['format']['timezone'])
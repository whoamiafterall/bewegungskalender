from typing import Final

import yaml

from bewegungskalender.backend.io.cli import CREDENTIALS_FILE
from bewegungskalender.libs.logger import LOGGER

# get Config from yml file
LOGGER.debug('Loading credentials file...')
try:
    with open(CREDENTIALS_FILE, 'r') as f:
        CREDENTIALS:dict = yaml.load(f, Loader=yaml.FullLoader)
except FileNotFoundError:
    LOGGER.exception('Credentials File not Found:', CREDENTIALS_FILE); exit()

# Nextcloud Section
NC_DOMAIN: Final[str] = CREDENTIALS['nextcloud']['domain']
NC_USR: Final[str] = CREDENTIALS['nextcloud']['username']
NC_PW: Final[str] = CREDENTIALS['nextcloud']['token']

# Mail Section
MAIL_SRV: Final[str] = CREDENTIALS['mail']['domain']
MAIL_PORT: Final[int] = CREDENTIALS['mail']['smtp_port']
MAIL_ACC: Final[str] = CREDENTIALS['mail']['account']
MAIL_PW: Final[str] = CREDENTIALS['mail']['password']

# Telegram-Section
TELEGRAM_TOKEN: Final[str] = CREDENTIALS['telegram']['token']
TELEGRAM_PRODUCTION: Final[str] = CREDENTIALS['telegram']['production_channel_id']
TELEGRAM_TEST: Final[str] = CREDENTIALS['telegram']['test_channel_id']

# Mastodon-Section
MASTODON_CLIENT_KEY: Final[str] = CREDENTIALS['mastodon']['client_key']
MASTODON_CLIENT_SECRET: Final[str] = CREDENTIALS['mastodon']['client_secret']
MASTODON_ACCESS_TOKEN: Final[str] = CREDENTIALS['mastodon']['access_token']
MASTODON_INSTANCE: Final[str] = CREDENTIALS['mastodon']['instance']

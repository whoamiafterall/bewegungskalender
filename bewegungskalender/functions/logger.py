from logging import getLogger, Logger, DEBUG, INFO, ERROR
from bewegungskalender.functions.cli import LOGLEVEL

# Get Logger and set log level
LOGGER:Logger = getLogger(__name__)
if LOGLEVEL is not None:
    if LOGLEVEL == 'debug':
        LOGGER.setLevel(DEBUG)
    elif LOGLEVEL == 'info':
        LOGGER.setLevel(INFO)
    elif LOGLEVEL == 'error':
        LOGGER.setLevel(ERROR)

import logging
from logging import getLogger, Logger, DEBUG, INFO, ERROR
from bewegungskalender.backend.io.cli import LOGLEVEL

# Get Logger and set log level
logging.basicConfig()
LOGGER:Logger = getLogger("Bewegungskalender")
match LOGLEVEL:
    case 'debug':
        LOGGER.setLevel(DEBUG)
    case 'info':
        LOGGER.setLevel(INFO)
    case 'error':
        LOGGER.setLevel(ERROR)
    case _:
        LOGGER.setLevel(INFO)
import logging
import time
from logging import getLogger, Logger, DEBUG, INFO, ERROR

from bewegungskalender.backend.io.cli import LOGLEVEL


class RelativeSeconds(logging.Formatter):
    def format(self, record):
        record.relativeCreated = record.relativeCreated // 1000
        return super().format(record)

formatter = RelativeSeconds("%(relativeCreated)ds %(levelname)s %(module)s.%(funcName)s:\n%(message)s")

# Get Logger and set log level
logging.basicConfig()
logging.root.handlers[0].setFormatter(formatter)
LOGGER:Logger = getLogger(__name__)
match LOGLEVEL:
    case 'debug':
        LOGGER.setLevel(DEBUG)
    case 'info':
        LOGGER.setLevel(INFO)
    case 'error':
        LOGGER.setLevel(ERROR)
    case _:
        LOGGER.setLevel(INFO)
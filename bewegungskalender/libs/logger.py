import logging
import time
from logging import Logger, DEBUG, INFO, ERROR
from typing import Sized

from bewegungskalender.backend.io.cli import LOGLEVEL

class RelativeSeconds(logging.Formatter):
    def format(self, record):
        record.relativeCreated = record.relativeCreated // 1000
        return super().format(record)
        
def log_status(ref_status, data: Sized, counter: int):
    exact_percent = 100 / ref_status['complete'] * ((ref_status['current'] - 1) + 1 / len(data) * counter)
    eta = "..." if exact_percent == 0 else round(
        (time.time() - ref_status['start_time']) / exact_percent * (100 - exact_percent))
    LOGGER.info(
        f"Category [{ref_status['current']}/{ref_status['complete']}] Event [{counter}/{len(data)}] - {round(exact_percent, 1)}% ETA: {eta}s")

formatter = RelativeSeconds("%(relativeCreated)ds %(levelname)s %(module)s.%(funcName)s:\n%(message)s")

# Get Logger and set log level
logging.basicConfig()
logging.root.handlers[0].setFormatter(formatter)
LOGGER: Logger = logging.getLogger(__name__)
match LOGLEVEL:
    case 'debug':
        LOGGER.setLevel(DEBUG)
    case 'info':
        LOGGER.setLevel(INFO)
    case 'error':
        LOGGER.setLevel(ERROR)
    case _:
        LOGGER.setLevel(INFO)
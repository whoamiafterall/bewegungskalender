import csv
import urllib.request
from datetime import datetime, timedelta

import pytz

from bewegungskalender.backend.calendar.client import DAVCLIENT
from bewegungskalender.backend.calendar.event import Event
from bewegungskalender.backend.io.cli import LAST_UPDATE
from bewegungskalender.backend.io.config import NCFORM_URL, INPUT_CALENDAR
from bewegungskalender.libs.logger import LOGGER


def update_ncform():
    LOGGER.info('Checking Nextcloud Form Responses for new events...')
    LOGGER.debug("Downloading CSV-File with Responses to NC-Form...")
    file = urllib.request.urlretrieve(NCFORM_URL, "bewegungskalender/data/nextcloud_form.csv")[0]
    calendar = DAVCLIENT.calendar(url=INPUT_CALENDAR)
    with open(file) as f:
        for row in csv.DictReader(f):
            if datetime.fromisoformat(row['Timestamp']) > datetime.now(tz=pytz.utc) - timedelta(LAST_UPDATE):
                event = Event.from_nextcloud_form(row)
                calendar.add_event(event.to_icalendar().to_ical())
                LOGGER.info(f"Successfully added {row['Start-Datum']}: {row['Titel']} to calender!")
            else:
                LOGGER.info(f"No Events found to add between {LAST_UPDATE} and now.")
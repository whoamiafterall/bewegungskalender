import csv
import caldav
import pytz
import urllib.request
from caldav import DAVClient
from bewegungskalender.functions.config import NCFORM_URL, INPUT_CALENDAR, CALDAV_URL, CALDAV_USR, CALDAV_PW
from datetime import datetime, timedelta
from bewegungskalender.functions.cli import LAST_UPDATE
from bewegungskalender.classes.event import Event
from bewegungskalender.functions.logger import LOGGER

def update_ncform():
    LOGGER.info('Checking Nextcloud Form Responses for new events...')
    LOGGER.debug("Downloading CSV-File with Responses to NC-Form...")
    file = urllib.request.urlretrieve(NCFORM_URL, "bewegungskalender/data/termine.csv")[0]
    davclient: DAVClient = caldav.DAVClient(url=CALDAV_URL, username=CALDAV_USR, password=CALDAV_PW)
    calendar = davclient.calendar(url=INPUT_CALENDAR)
    with open(file) as f:
        for row in csv.DictReader(f):
            if datetime.fromisoformat(row['Timestamp']) > datetime.now(tz=pytz.utc) - timedelta(LAST_UPDATE):
                event = Event.from_nextcloud_form(row).to_icalendar()
                calendar.add_event(event.to_ical())
                LOGGER.info(f"Successfully added {row['Start-Datum']}: {row['Titel']} to calender!")
            else:
                LOGGER.info(f"No Events found to add between {LAST_UPDATE} and now.")
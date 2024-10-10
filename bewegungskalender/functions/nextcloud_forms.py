import csv
import pytz
import urllib.request
from caldav import Calendar
from datetime import datetime, timedelta
from bewegungskalender.functions.cli import LAST_UPDATE
from bewegungskalender.functions.event import Event
from bewegungskalender.functions.logger import LOGGER

def update_ncform(url:str, calendar:Calendar):
    LOGGER.info('Checking Nextcloud Form Responses for new events...')
    LOGGER.debug("Downloading CSV-File with Responses to NC-Form...")
    file = urllib.request.urlretrieve(url, "bewegungskalender/data/termine.csv")[0]
    with open(file) as f:
        for row in csv.DictReader(f):
            if datetime.fromisoformat(row['Timestamp']) > datetime.now(tz=pytz.utc)- timedelta(LAST_UPDATE):
                event = Event.from_nextcloud_form(row).to_icalendar()
    calendar.add_event(event.to_ical())
    LOGGER.info(f"Successfully added {row['Start-Datum']}: {row['Titel']} to calender!")
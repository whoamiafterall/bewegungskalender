import csv
import logging
import icalendar
import pytz
import urllib.request
from caldav import Calendar
from datetime import datetime, timedelta
from bewegungskalender.helper.cli import args

def update_ncform(url:str, calendar:Calendar) -> dict:
    logging.info('Checking Nextcloud Form Responses for new events...')
    logging.debug("Downloading CSV-File with Responses to NC-Form...")
    file = urllib.request.urlretrieve(url, "bewegungskalender/data/termine.csv")[0]
    with open(file) as f:
        for row in csv.DictReader(f):
            if datetime.fromisoformat(row['Timestamp']) > datetime.now(tz=pytz.utc) - timedelta(args.update_ncform):
                create_events(row, calendar)
            
def create_events(row:dict, calendar:Calendar):
    event = icalendar.Event()
    event.add('summary', f"{row['Titel']} ({row['Stadt/Region']})")
    event.add('location', row['Adresse'])
    event.add('description', f"{row['Link']}\n{row['Beschreibung (lang)']}")
    # Handle Start of Event
    if row['Start-Zeit'] != "":
        start = datetime.strptime(f"{row['Start-Datum']}-{row['Start-Zeit']}", '%Y-%m-%d-%H:%M') 
    else: # When start-time is None
        start = datetime.strptime(row['Start-Datum'], '%Y-%m-%d')
    event.add('dtstart', start)
    # Handle End of Event
    if row['End-Datum'] != "" and row['End-Uhrzeit'] != "":
        end = datetime.strptime(f"{row['End-Datum']}-{row['End-Uhrzeit']}", '%Y-%m-%d-%H:%M') 
    elif row['End-Datum'] != "": # When end-time is None
        end = datetime.strptime(row['End-Datum'], '%Y-%m-%d')
    else: # When both end-date and end-time are None
        end = datetime.combine(start.date() + timedelta(1), datetime.min.time())
    event.add('dtend', end)
    calendar.add_event(event.to_ical())
    logging.info(f"Successfully added {row['Start-Datum']}: {row['Titel']} to calender!")
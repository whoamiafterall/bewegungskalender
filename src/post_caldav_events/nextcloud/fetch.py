import caldav
import icalendar
from collections import namedtuple
from post_caldav_events.helper.datetime import check_datetime, days, to_timezone, date, fix_midnight
    
def connect_davclient(config:dict):
    return caldav.DAVClient(url=config['caldav']['url'], username=config['caldav']['username'], password=config['caldav']['password'])    

def get_calendar_name(calendar:caldav.Calendar):
    return calendar.get_properties([caldav.dav.DisplayName()])['{DAV:}displayname']

def parse_event_data(event):
    start = to_timezone(check_datetime(event.get('dtstart').dt))
    end = to_timezone(check_datetime(event.get('dtend').dt))
    if date(start) != date(end):
        end = fix_midnight(end)
    values = {
        'summary': event.get('summary'),
        'description': event.get('description'),
        'location': event.get('location'),
        'start': start, 
        'end': end,
        'recurrence': event.get('recurrence-id')
        }
    return values

def date_search(calendar:caldav.Calendar, querystart, queryend):
    events = []
    for cal_data in calendar.date_search(querystart, queryend):
        ical_data = icalendar.Event.from_ical(cal_data.data)
        for component in ical_data.walk():
            if component.name == "VEVENT":
                events.append(parse_event_data(component))
    return events
                
def fetch_events(config: dict, querystart: int, queryend: int, data = []) -> dict:
    """
    Reads calendars specified in config using a CalDAV client.
    Fetches events from Nextcloud calendar by calendar using date_search.
    Returns a dict with an Array of Events mapped to each calendars name (string).
    """
    try:
        davclient = connect_davclient(config) 
    except ConnectionError:
        print("Connection to Nextcloud failed.")
        exit()
    for configline in config['calendars']:
        calendar = namedtuple("calendar", ["emoji", "name", "events"])
        url = davclient.calendar(url=configline['calendar']['url'])
        events = date_search(url, querystart, queryend)
        calendar.name = get_calendar_name(url)
        calendar.events = (sorted([e for e in events], key=lambda d:d['start']))
        calendar.emoji = configline['calendar']['emoji']
        data.append(calendar)
    return data
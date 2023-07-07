import datetime
import locale
import caldav
import icalendar
import pytz

timezone = ""

def to_datetime(date:datetime.date):
    return date if isinstance(date, datetime.datetime) else datetime.datetime.combine(date, datetime.datetime.min.time()).astimezone(timezone)

def set_locale(config:dict):
    locale.setlocale(locale.LC_TIME, config['format']['time_locale'])   

def set_timezone(config:dict):
    global timezone
    timezone = pytz.timezone(config['format']['timezone'])
    
def get_calendar_name(calendar:caldav.Calendar):
    return calendar.get_properties([caldav.dav.DisplayName()])['{DAV:}displayname']

def parse_event_data(vevent):
    start = to_datetime(vevent.get('dtstart').dt)
    try:
        end = to_datetime(vevent.get('dtend').dt)
    except AttributeError:
        end = None
    if start.date is not end.date:
        end = end - datetime.timedelta(days=1)
    values = {
        'summary': vevent.get('summary'),
        'description': vevent.get('description'),
        'location': vevent.get('location'),
        'start': start, 
        'end': end,}
    return values

def date_search(calendar:caldav.Calendar, querystart, queryend):
    events = []
    for cal_data in calendar.date_search(querystart, queryend):
        ical_data = icalendar.Event.from_ical(cal_data.data)
        for component in ical_data.walk():
            if component.name == "VEVENT":
                events.append(parse_event_data(component))
    return events
                
def fetch_events(config: dict, querystart: int, queryend: int) -> dict:
    """y
    Reads calendars specified in config.
    Fetches events from Nextcloud calendar by calendar using date_search.
    Returns a dict with an Array of Events mapped to each calendars name (string).
    See also "append_event" method to see which attributes are fetched of each event.
    """
    try:
        davclient = caldav.DAVClient(url=config['caldav']['url'], username=config['caldav']['username'], password=config['caldav']['password']) 
    except ConnectionError:
        print("Connection to Nextcloud failed.")
        exit()
    event_lists = []
    calendar_names = []
    for caldavline in config['caldav']['calendars']:
        calendar = davclient.calendar(url=caldavline['url'])
        calendar_names.append(get_calendar_name(calendar))
        events = date_search(calendar, querystart, queryend)
        event_lists.append(sorted([e for e in events], key=lambda d:d['start']))
    return dict(zip(calendar_names, event_lists))
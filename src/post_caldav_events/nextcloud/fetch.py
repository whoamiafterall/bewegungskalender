import caldav
import icalendar
from post_caldav_events.helper.datetime import check_datetime, days
    
def get_calendar_name(calendar:caldav.Calendar):
    return calendar.get_properties([caldav.dav.DisplayName()])['{DAV:}displayname']

def parse_event_data(event):
    start = check_datetime(event.get('dtstart').dt)
    end = check_datetime(event.get('dtend').dt)
    if start.date is not end.date:
        end = end - days(1)
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
                
def fetch_events(config: dict, querystart: int, queryend: int) -> dict:
    """
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
    for calendar in config['calendars']:
        url = davclient.calendar(url=calendar['calendar']['url'])
        events = date_search(url, querystart, queryend)
        if events != []:
            event_lists.append(sorted([e for e in events], key=lambda d:d['start'])) 
            calendar_names.append(calendar['calendar']['emoji'] + " " + get_calendar_name(url))
    return dict(zip(calendar_names, event_lists))
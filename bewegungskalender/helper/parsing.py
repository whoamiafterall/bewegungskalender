from collections import namedtuple
from html.parser import HTMLParser
import logging
from typing import NamedTuple
from bewegungskalender.helper.datetime import check_datetime, date, fix_midnight, to_timezone
import icalendar

def parse_event(component:icalendar.Event)-> NamedTuple:
    # Parse Data from icalendar format to NamedTuple
    event = namedtuple("event", ["summary", "description", "location", "start", "end", "recurrence"])
    event.summary =  component.get('summary')
    event.description = component.get('description')
    event.location = component.get('location')
    event.start = to_timezone(check_datetime(component.get('dtstart').dt))
    event.end = to_timezone(check_datetime(component.get('dtend').dt))
    event.recurrence = component.get('recurrence-id')
    
    # Fix Events that end on midnight being read as one day longer than they are
    if date(event.start) != date(event.end):
        event.end = fix_midnight(event.end)
        
    logging.debug(f"Success parsing {event.summary}...")
    return event   

class ParseWPForms(HTMLParser):
    isformdata = bool; formdata = []
    def handle_data(self, data):
        if self.isformdata == True: self.formdata.append(data)

    def handle_starttag(self, tag: str, attrs: list):
        if tag == "td": 
            for name, value in attrs: 
                if name == 'style': 
                    if value == "color:#555555;padding-top: 3px;padding-bottom: 20px;": self.isformdata = True

    def handle_endtag(self, tag: str) -> None:
        if tag == "td": self.isformdata = False

    def parse(self, data) -> list:
        self.feed(data); return self.formdata
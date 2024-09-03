from datetime import datetime
from enum import Enum
import logging
import os
import re
from typing import Tuple
from bewegungskalender.helper.datetime import time, date

class Format(Enum):
    HTML = 'html'
    MD = 'markdown'
    TXT = 'txt'

# generic functions for handling different text formatting

def newline():
    return "\n"

def bold(text:str, mode: Format) -> str:
    return "<b> " + text + " </b>" if mode == Format.HTML else ("*" + text + "*")

def italic(text:str, mode: Format) -> str:
    return "<i> " + text + " </i>" if mode == Format.HTML else ("_" + text + "_")
    
def escape_markdown(text:str) -> str:
    if text is None:
        return ""
    charset = "?_–*[]()~`>#+-=|.!'{''}''"
    translate_dict = {c: "\\" + c for c in charset}
    return text.translate(str.maketrans(translate_dict))

def search_link(summary:str, description:str) -> str:
    if  description is not None:
        try: 
            return re.search("(?P<url>https?://[^\s]+)", description).group("url") 
        except AttributeError: 
            logging.warn(f"L: {summary}: No Link in: {description}")
            return None
    
def md_link(text:str, url:str) -> str:
    if search_link(text, url) is not None:
        return f" [{escape_markdown(text)}]({search_link(text, url)})"
    else:
        return f" {escape_markdown(text)}"

def match_and_add_recurring(event:Tuple, message:str, mode:Format) -> str:
    # Prepare regex, the primary entry of the event and the date to add if its not the first occurence
    if mode == Format.TXT:
        regex = r'(\d{2}\.\d{2}\.\s)(\(\d{2}\:\d{2}\)\:\s)?' + f"({re.escape(event.summary)})"
        event_string = eventtime(event.start, event.end) + f" {event.summary}"
        date_to_add = f"& {date(event.start)} "
    elif mode == Format.MD or Format.HTML:
        regex = r'(\d{2}\\\.\d{2}\\\.\s)(\\\(\d{2}\:\d{2}\\\)\:\s)?' + f"(\[{re.escape(escape_markdown(event.summary))}\])"
        event_string =  escape_markdown(eventtime(event.start, event.end)) + md_link(event.summary, event.description)
        date_to_add =  f"& {escape_markdown(date(event.start))} "
    
    match = re.search(regex, message) # Try to match the event in the existing message
    if match is None:                 # If it's the first occurence, add the primary entry of the event and return
        return message + event_string + "\n"
    else:                             # If it's not the first occurence add just the date and return
        return add_recurring_date(date_to_add, match, message)

def add_recurring_date(date_to_add:str, match:re.Match, message:str) -> str:
        if match.group(2) is None:
            substitute = match.group(1) + date_to_add + match.group(3)
        else:
            substitute = match.group(1) + date_to_add + match.group(2) + match.group(3)
        return message[:match.span()[0]] + substitute + message[match.span()[1]:]

def to_filename(text):
    text = text.replace(' ', '_')
    return os.path.basename(text)

def eventtime(start:datetime, end:datetime) -> str:
    if time(start) == "(00:00)" and date(start) != date(end):
        return f"{date(start)} - {date(end)}"
    elif time(start) == "(00:00)" and date(start) == date(end):
        return f"{date(start):}"
    return f"{date(start)} {time(start)}:"
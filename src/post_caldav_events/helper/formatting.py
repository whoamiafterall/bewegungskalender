from enum import Enum
import re
from post_caldav_events.helper.datetime import eventtime

class Format(Enum):
    HTML = 'html'
    MD = 'markdown'
    TXT = 'txt'

# generic functions for handling different text formatting

def newline():
    return "\n"

def bold(text:str, mode: Format) -> str:
    return "<b> " + text + " </b>" if mode == Format.HTML else ("*" + text + "*" if mode == Format.MD else text)

def italic(text:str, mode: Format) -> str:
    """
    Returns the given string in italic.
    
    Args:
        text (string): The string that shall be written in italic characters.
        mode (Format): The formatting mode to use.
    """    
    return "<i> " + text + " </i>" if mode == Format.HTML else ("_" + text + "_" if mode == Format.MD else text)
    
def escape_chars(text:str) -> str:
    """
    escape characters to use markdown
    """
    if text is None:
        return ""
    escape_chars = "?_–*[]()~`>#+-=|.!'{''}''"
    translate_dict = {c: "\\" + c for c in escape_chars}
    return text.translate(str.maketrans(translate_dict))

def search_link(description:str) -> str:
    if  description is not None:
        try: return re.search("(?P<url>https?://[^\s]+)", description).group("url") 
        except AttributeError: return print(f"L: No Link found in: {description}")
    
def md_link(text:str, url:str) -> str:
    return f" [{escape_chars(text)}]({search_link(url)})" if search_link(url) is not None else f" {escape_chars(text)}"; print(f"No valid link in description of event:{text}")

def match_string(string:str, text:str, mode) -> str:
    regex = '\.\s.*'
    regex += re.escape(escape_chars(f"{string}") if mode == Format.HTML or Format.MD else f"\..*{string}")
    return re.search(regex, text)

def md_event(event:dict) -> str:
    return escape_chars(eventtime(event['start'], event['end'])) + md_link(event['summary'], event['description'])

def txt_event(event:dict) -> str:
    return eventtime(event['start'], event['end']) + f" {event['summary']}"  

def add_event(event:dict, mode:Format):
    return md_event(event) if mode == Format.MD or Format.HTML else txt_event(event)
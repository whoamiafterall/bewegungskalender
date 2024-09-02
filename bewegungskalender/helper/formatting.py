from datetime import datetime
from enum import Enum
import logging
import os
import re
from bewegungskalender.helper.datetime import date, time

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


def match_string(string:str, text:str, mode) -> re.Match|None:
    regex = '\.\s.*'
    regex += re.escape(escape_markdown(f"{string}") if mode == Format.HTML or Format.MD else f"{string}")
    return re.search(regex, text)

def to_filename(text):
    text = text.replace(' ', '_')
    return os.path.basename(text)

def eventtime(start:datetime, end:datetime) -> str:
    if time(start) == "(00:00)" and date(start) != date(end):
        return f"{date(start)} - {date(end)}"
    elif time(start) == "(00:00)" and date(start) == date(end):
        return f"{date(start):}"
    return f"{date(start)} {time(start)}:"


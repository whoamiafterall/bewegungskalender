from _datetime import datetime
from enum import Enum
import os
import re
from typing import Tuple
from bewegungskalender.functions.datetime import date_str, time
from bewegungskalender.functions.event import Event
from bewegungskalender.functions.logger import LOGGER

class Format(Enum): # to make dot notation available
    HTML = 'html'
    MD = 'markdown'
    TXT = 'txt'
    
class Style(Enum):
    BOLD = 'bold'
    ITALIC = 'italic'
    CODE = 'code'
    STRIKETHROUGH = 'strikethrough'
    UNDERLINE = 'underline'
    HIGHLIGHT = 'highlight'

# generic functions for handling different text formatting
def newline() -> str:
    """Returns a newline statement ('\n'). Useful to reuse when templating content.

    Returns:
        str: '\n' => the newline statement
    """    
    return "\n"

def style(text:str, format: Format, style:Style) -> str:
    """Styles the given text in the given format with the given style. 

    Args:
        text (str): The text to be styled.
        format (Format): The format to be used. See Format Class.
        style (Style): The style to be used. See Style Class.

    Returns:
        str: The styled **text** in the given format with the given style.
    """    
    if format == Format.TXT:
        return
    match style:
        case Style.BOLD:
            return "<b> " + text + " </b>" if format == Format.HTML else ("*" + text + "*")
        case Style.ITALIC:
            return "<i> " + text + " </i>" if format == Format.HTML else ("_" + text + "_")
        case Style.CODE:
            return "<code> " + text + " </code>" if format == Format.HTML else ("`" + text + "`")
        case Style.STRIKETHROUGH:
            return "<s> " + text + " </s>" if format == Format.HTML else ("~~" + text + "~~")
        case Style.UNDERLINE:
            return "<u> " + text + " </u>"
        case Style.HIGHLIGHT:
            return "<mark> " + text + " </mark>" if format == Format.HTML else ("==" + text + "==")
               
             
def escape(text:str, charset:str = "?_–*[]()~`>#+-=|.!'{''}''" ) -> str:
    """Escapes characters from a given charset in a given string with `\\\`'. <br>
    The default charset escapes all relevant characters for **Markdown and HTML** formatting.
    
    Args:
        text (str): The text where characters should be escaped with `\\\`.
        charset (str): The characters to be escaped. Defaults to: "?_–*[]()~`>#+-=|.!'{''}''" 

    Returns:
        str: The given text with the only change that the given characters are escaped with `\\\`.
    """    
    if text is None:
        return ""
    # Add "\\" in front of each character in the charset and return
    translate_dict = {c: "\\" + c for c in charset} 
    return text.translate(str.maketrans(translate_dict))

def search_link(summary:str, description:str) -> str:
    if  description is not None:
        try: # 
            return re.search("(?P<url>https?://[^\s]+)", description).group("url") 
        except AttributeError: 
            LOGGER.warning(f"L: {summary}: No Link in: {description}")
            return None
    
def md_link(text:str, url:str) -> str:
    if search_link(text, url) is not None:
        return f" [{escape(text)}]({search_link(text, url)})"
    else:
        return f" {escape(text)}"

def match_and_add_recurring(event:Event, message:str, format:Format) -> str:
    # Prepare regex, the primary entry of the event and the date to add if its not the first occurence
    if format == Format.TXT:
        regex = r'(\d{2}\.\d{2}\.\s)(\(\d{2}\:\d{2}\)\:\s)?' + f"({re.escape(event.summary)})"
        event_string = eventtime(event.start, event.end) + f" {event.summary}"
        date_to_add = f"& {date_str(event.start)} "
    elif format == Format.MD or Format.HTML:
        regex = r'(\d{2}\\\.\d{2}\\\.\s)(\\\(\d{2}\:\d{2}\\\)\:\s)?' + f"(\[{re.escape(escape(event.summary))}\])"
        event_string =  escape(eventtime(event.start, event.end)) + md_link(event.summary, event.description)
        date_to_add =  f"& {date_str(event.start)} "
    
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
    if time(start) == "(00:00)" and start.date() != end.date():
        return f"{date_str(start)} - {date_str(end)}"
    elif time(start) == "(00:00)" and start.date() == end.date():
        return f"{date_str(start):}"
    return f"{date_str(start)} {time(start)}:"
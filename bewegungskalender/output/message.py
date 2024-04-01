import collections
import datetime
import logging
import markdown
from collections import namedtuple
from bewegungskalender.helper.datetime import weekday_date, date
from bewegungskalender.helper.formatting import md_link, escape_chars, bold, newline, Format, match_string, add_event

# Functions that produce some type of message content
def queryline(query_start: datetime, query_end: datetime, mode: Format): # Displayed as Head of the Message
    return bold(escape_chars(f"Die Termine vom " + weekday_date(query_start) + " - " + weekday_date(query_end) + "\n"), mode)

def footer(config:dict, mode: Format):
    footer = bold("🌐 Links \n", mode)
    for item in config['links']:
        footer += md_link(escape_chars(item['link']['text']), item['link']['url']) + "\n"
    return footer       

def recurring_event(event: namedtuple, message:str, mode:Format) -> str:
    entry = match_string(event.summary, message, mode)
    if entry is None:
        message += add_event(event, mode)
        message += newline()
        return message
    else:
        index = message.find(entry.group())
        return message[:index+2] + f"& {escape_chars(date(event.start))} " + message[index+2:] 
    
# Forms Titles out of Calendar Names (Categories) - set by config - adds bold for HTML.
def calendar_title(emoji: str, name: str, mode: Format) -> str: 
    if mode == Format.MD:
        name = escape_chars(name) 
    title = f"{emoji} {name}"
    return bold(title, mode)  

def message(config:dict, data:list, querystart: datetime, queryend: datetime, mode:Format) -> str:
    """
    
    """
    message = queryline(querystart, queryend, mode)
    for calendar in data:
        logging.debug(f"Formatting {calendar.name} to {mode}...")
        if calendar.events != []:
            message += newline()
            message += calendar_title(calendar.emoji, calendar.name, mode) 
            message += newline()
            for event in calendar.events:
                if event.recurrence is not None:
                    message = recurring_event(event, message, mode)
                else:
                    message += add_event(event, mode)
                    message += newline()
    message += newline()
    message += footer(config, mode)
    logging.info(f"Successfully formatted the message to {mode}!")
    return markdown.markdown(message.strip(), extensions=['nl2br']) if mode == Format.HTML else message.strip()
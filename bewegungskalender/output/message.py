import datetime
import logging
import markdown
from collections import namedtuple
from bewegungskalender.helper.datetime import weekday_date, date
from bewegungskalender.helper.formatting import md_link, escape_chars, bold, newline, Format, match_string, add_event

def queryline(start: datetime.date, stop: datetime.date, mode: Format): # Displayed as Head of the Message
    return bold(escape_chars(f"Die Termine vom " + weekday_date(start) + " - " + weekday_date(stop) + "\n"), mode)

def footer(config:dict, mode: Format) -> str:
    footer:str = bold("🌐 Links \n", mode)
    for item in config['links']:
        footer += md_link(escape_chars(item['link']['text']), item['link']['url']) + "\n"
    return footer       

def recurring_event(event: namedtuple, message:str, mode:Format) -> str:
    entry:str = match_string(event.summary, message, mode)
    if entry is None:
        message += add_event(event, mode)
        message += newline()
        return message
    else:
        index:int = message.find(entry.group())
        logging.debug(f"Recurring Event: {event.summary} - adding date to line in message")
        return message[:index+2] + f"& {escape_chars(date(event.start))} " + message[index+2:] 
    
# Forms Titles out of Calendar Names (Categories) - set by config - adds bold for HTML.
def calendar_title(emoji: str, name: str, mode: Format) -> str: 
    if mode == Format.MD:
        name:str = escape_chars(name) 
    title:str = f"{emoji} {name}"
    return bold(title, mode)  

def message(config:dict, data:list, start: datetime.date, stop: datetime.date, mode:Format) -> str:
    message:str = queryline(start, stop, mode)
    for calendar in data:
        logging.debug(f"Formatting {calendar.name} to {mode}...")
        if calendar.events != []:
            message += newline()
            message += calendar_title(calendar.emoji, calendar.name, mode) 
            message += newline()
            for event in calendar.events:
                if event.recurrence is not None:
                    message:str = recurring_event(event, message, mode)
                else:
                    message += add_event(event, mode)
                    message += newline()
    message += newline()
    message += footer(config, mode)
    logging.info(f"Successfully formatted the message to {mode}!")
    return markdown.markdown(message.strip(), extensions=['nl2br']) if mode == Format.HTML else message.strip()
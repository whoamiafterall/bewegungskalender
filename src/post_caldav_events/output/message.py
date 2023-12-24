import datetime
import markdown
from post_caldav_events.helper.datetime import time, weekday_date, date
from post_caldav_events.helper.formatting import markdown_link, markdownify, bold, italic, newline, match_string, Format

# functions that produce some type of generic message content

def queryline(query_start: datetime, query_end: datetime, mode: Format): # Displayed as Head of the Message
    return bold(markdownify(f"Die Termine vom " + weekday_date(query_start) + " - " + weekday_date(query_end) + "\n"), mode)

def footer(config:dict, mode: Format):
    footer = bold("🌐 Links \n", mode)
    for item in config['links']:
        footer += markdown_link(markdownify(item['link']['text']), item['link']['url']) + "\n"
    return footer

# Forms Titles out of Calendar Names (Categories) - set by config - adds bold for HTML.
def calendar_title(calendar_name: str, mode: Format) -> str: 
    if mode == Format.MD:
        calendar_name = markdownify(calendar_name) 
    return bold(calendar_name, mode)

def md_event(event:dict) -> str:
    return markdownify(eventtime(event['start'], event['end'])) + markdown_link(event['summary'], event['description'])

def txt_event(event:dict) -> str:
    return eventtime(event['start'], event['end']) + f" {event['summary']}"

def eventtime(start:datetime, end:datetime) -> str:
    if start == end or (start + datetime.timedelta(days=1)) == end:
        return f"{date(start)}" if time(start) == "(00:00)" else f"{date(start)} {time(start)}:"
    else:
        if time(start) == "(00:00)":
            return f"{date(start)} - {date(end)}"
        return f"{date(start)} - {date(end)}" if start + datetime.timedelta(days=1) < end else f"{date(start)} {time(start)}:"

def recurring(event:dict, message:str, mode:Format) -> str:
    entry = match_string(event['summary'], message, mode)
    if entry is None:
        message += md_event(event) if mode == Format.MD or Format.HTML else txt_event(event)
        message += newline()
        return message
    else:
        index = message.find(entry.group())
        return message[:index+2] + f"& {markdownify(date(event['start']))} " + message[index+2:]        
    
def message(config:dict, events:dict, querystart: datetime, queryend: datetime, mode:Format) -> str:
    """
    
    """
    message = queryline(querystart, queryend, mode)
    for calendar_name, event_list in events.items():
        message += newline()
        message += calendar_title(calendar_name, mode) 
        message += newline()
        for event in event_list:
            if event['recurrence'] is not None:
                message = recurring(event, message, mode)
            else:
                if mode == Format.HTML or Format.MD:
                    message += md_event(event)
                else:  
                    message += txt_event(event)   
                message += newline()
    message += newline()
    message += footer(config, mode)
    return markdown.markdown(message.strip(), extensions=['nl2br']) if mode == Format.HTML else message.strip()
     
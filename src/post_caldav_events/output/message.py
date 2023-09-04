import re
import datetime
import markdown
from post_caldav_events.datetime import time, weekday, date

def newline():
    return "\n"

def header(query_start, query_end): # Displayed as Head of the Message
    return f"📅 " + weekday(query_start) + " " + date(query_start) + " - " + weekday(query_end) + " " + date(query_end) + "\n" 

def footer(config:dict): # Displayed at the End of the Message - set by config
    text = ""
    for line in config['message']['footer']:
        text += line['line']
        text += "\n"
    return text

def emoji(name, config:dict): # Adds Emojis in front of Calendar Titles (Categories) - set by config
    for calendar, emoji in config['message']['emojis']:
        if name == calendar:
            return emoji + " "
        else:
            return "🔎 "

def link(description:str):
    if  description is not None:
        try: return re.search("(?P<url>https?://[^\s]+)", description).group("url") 
        except AttributeError: return
    
def markdown_title_link(event: dict):
    summary = markdownify((event['summary']))
    if link(event['description']) is not None:
        return f" [{summary}]({link(event['description'])})" 
    else: return f" {summary}"

def eventtime(start:datetime, end:datetime):
    if start == end or (start + datetime.timedelta(days=1)) == end:
        if time(start) == "(00:00)":
            return f"{date(start)}"
        return f"{date(start)} {time(start)}:"
    else:
        if time(start) == "(00:00)":
            return f"{date(start)} - {date(end)}"
        elif start + datetime.timedelta(days=1) < end:
            return f"{date(start)} - {date(end)}"
        return f"{date(start)} {time(start)}:"
    
def recurring(event:dict, message:str, mode:['plain','md','html']):
    regex = '\.\s.*'
    regex += re.escape(markdownify(f"{event['summary']}") if mode in ['md', 'html'] else f"\..*{event['summary']}")
    entry = re.search(regex, message)
    if entry is None:
        message += markdownify(eventtime(event['start'], event['end'])) + markdown_title_link(event) if mode in ['md','html'] else eventtime(event['start'], event['end']) + f" {event['summary']}"
        message += newline()
        return message
    else:
        index = message.find(entry.group())
        return message[:index+2] + f"& {markdownify(date(event['start']))} " + message[index+2:]
        
    
def markdownify(text: str):
    """
    escape characters to use markdown
    """
    if text is None:
        return ""
    escape_chars = "?_–*[]()~`>#+-=|.!'{''}''"
    translate_dict = {c: "\\" + c for c in escape_chars}
    return text.translate(str.maketrans(translate_dict))
    
def message(config:dict, events:dict, querystart: int, queryend: int, mode:['plain','md','html']):
    """
    
    """
    message = markdownify(header(querystart, queryend)) if mode in ['md','html'] else header(querystart, queryend)
    for calendar_name, event_list in events.items():
        if event_list == []:
            continue
        message += newline()
        message += emoji(calendar_name, config) + f"{markdownify(calendar_name)}" if mode in ['md','html'] else emoji(calendar_name, config) + calendar_name
        message += newline()
        for event in event_list:
            if event['recurrence'] is not None:
                message = recurring(event, message, mode)
            else:
                message += markdownify(eventtime(event['start'], event['end'])) + markdown_title_link(event) if mode in ['md','html'] else eventtime(event['start'], event['end']) + f" {event['summary']}"
                message += newline()
    message += newline()
    message += footer(config)
    return markdown.markdown(message.strip(), extensions=['nl2br']) if mode == 'html' else message.strip()
    
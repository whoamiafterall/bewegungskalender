import re
import datetime
from post_caldav_events.nextcloud.fetch import get_queryend, get_querystart

def header(config:dict):
    header = f"📅 Die Termine vom " + date(get_querystart(config)) + " bis " + date(get_queryend(config,  get_querystart(config))) + "\n"
    return header

def emoji(name:str):
    emojis = {
        'Konferenzen & Treffen': '👥 ',
        'Aktionstage & Demos': '🟢 ',
        'Jahres & Gedenktage': '🟠 ',
        'Prozesse & Repression': '🟡 ',
        'System-Events & Termine': '🔴 ',
        'Camps & Festivals': '🔵 ',
        'Workshops & Skillshares': '🟣 ',
    }
    return emojis.get(name, '🔍 ')

def footer():
    footer = "📅 Weitere Termine:\n"
    footer += "[\- Monatsansicht](https://cloud.systemli.org/apps/calendar/p/zJsbBZJSQLCfkSsQ-gGA9ttt2T6PQgcKq-Brn9ook4EJWMx3ki-a7nAXkDxDETZJm58-df5QdyrBKa6H9Kpa-NpegYZLCqZjpxMa2-Rgk2wiaFQtLXGa5W-GeG6jNfCLSENW2Fs/dayGridMonth/now)\n"
    footer += "[\- Listenansicht](https://cloud.systemli.org/apps/calendar/p/zJsbBZJSQLCfkSsQ-gGA9ttt2T6PQgcKq-Brn9ook4EJWMx3ki-a7nAXkDxDETZJm58-df5QdyrBKa6H9Kpa-NpegYZLCqZjpxMa2-Rgk2wiaFQtLXGa5W-GeG6jNfCLSENW2Fs/listMonth/now)\n"
    footer += "🌐 Dein Termin steht nicht drin?:\n"
    footer += "[\- Website \(mit Formular zum Termine eintragen\)](https://klimax.online/bewegungskalender)\n"
    footer += "[\- Andere Kalender\-Projekte](https://pad.kanthaus.online/s/Bewegungskalender#Weitere-Kalender)\n"
    footer += "[\- Mitmachen](https://pad.kanthaus.online/s/Bewegungskalender#Mitmachen-und-selbst-eintragen)\n"
   # footer += "[\- Matrix\-Kanal](https://matrix.to/#/#bewegungskalender:matrix.org) \=\> [Matrix\-Einführung](https://kurzelinks.de/matrix-intro)\n"
    return footer

def date(day:datetime.date):
    return day.strftime('%a') + " " + day.strftime('%d.%m')

def summary(summary:str):
    return "?" if summary is None else summary

def link(description:str):
    if  description is not None:
        try: return re.search("(?P<url>https?://[^\s]+)", description).group("url") 
        except AttributeError: return

def newline():
    return "\n"

def string(date:datetime.date, format):
    return date.astimezone().strftime(format)
    
def endtime(start:datetime, end:datetime):
    if start == end or (start + datetime.timedelta(days=1)) == end:
        return None
    elif (start + datetime.timedelta(days=1)) > end:
        return string(end, '%H:%M')
    else:
        return string(end, '%d.%m')
    
def markdown_title_link(event: dict):
    sum = markdownify(summary(event['summary']))
    if link(event['description']) is not None:
        return f" [{sum}]({link(event['description'])})" 
    else: return f" {sum}"

def time(event: dict):
    end = endtime(event['start'], event['end'])
    startday = string(event['start'], '%d.%m')
    time = string(event['start'], '%H:%M')
    if time == end or end == None:
        if time == "00:00":
            return f"{startday}"
        return f"{startday}, {time}"
    else:
        if time == "00:00":
            return f"{startday} - {end}"
        return f"{startday} ({time} - {end})"
   
def markdownify(text: str):
    """
    escape characters to use markdown
    """
    if text is None:
        return ""
    escape_chars = "?_–*[]()~`>#+-=|.!'{''}''"
    translate_dict = {c: "\\" + c for c in escape_chars}
    return text.translate(str.maketrans(translate_dict))
    
def message(events:dict, config:dict, markdown:bool):
    """
    
    """
    message = markdownify(header(config)) if markdown else header(config)
    for calendar_name, event_list in events.items():
        if event_list == []:
            continue
        message += newline()
        message += emoji(calendar_name) + f"{markdownify(calendar_name)}" if markdown else calendar_name
        message += newline()
        for event in event_list:
                message += markdownify(time(event)) + markdown_title_link(event) if markdown else time(event) + f" {event['summary']}"
                message += newline()
    message += newline()
    message += footer()
    return message.strip()
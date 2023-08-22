import re
import datetime
import markdown

def header(query_start, query_end):
    header = f"📅 Die Termine von " + date(query_start) + " bis " + date(query_end) + "\n"
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
    footer = "🗓️ [Monatsansicht öffnen \(alle Termine\)](https://cloud.systemli.org/apps/calendar/p/zJsbBZJSQLCfkSsQ-gGA9ttt2T6PQgcKq-Brn9ook4EJWMx3ki-a7nAXkDxDETZJm58-df5QdyrBKa6H9Kpa-NpegYZLCqZjpxMa2-Rgk2wiaFQtLXGa5W-GeG6jNfCLSENW2Fs/dayGridMonth/now)\n"
    footer += "🗺️ [Karte öffnen \(Termine der nächsten 3 Monate\)](https://umap.openstreetmap.de/en/map/bewegungskalender-karte_42841#5/50.219/7.339)\n"
    footer += "🌐 [Website \(mit Formular zum Termine eintragen\)](https://klimax.online/bewegungskalender)\n"
    footer += "\[m\] [In der Matrix finden](https://matrix.to/#/#bewegungskalender:matrix.org) \=\> [\(Matrix\-Einführung\)](https://pad.kanthaus.online/s/Matrix-Einfuehrung#)\n"
    footer += "📩 [Mail\-Newsletter abonnieren](https://klimax.online/bewegungskalender/#Newsletter)\n"
    footer += "🔎 [Weitere Kalender finden](https://pad.kanthaus.online/s/Bewegungskalender#Weitere-Kalender)\n"
  #  footer += "❓ [FAQ](https://pad.kanthaus.online/s/Bewegungskalender)\n"
    return footer

def date(day:datetime.date):
    return day.strftime('%a.') + " " + day.strftime('%d.%m.')

def link(description:str):
    if  description is not None:
        try: return re.search("(?P<url>https?://[^\s]+)", description).group("url") 
        except AttributeError: return

def newline():
    return "\n"

def string(date:datetime.date, format):
    return date.astimezone().strftime(format)
    
def markdown_title_link(event: dict):
    summary = markdownify((event['summary']))
    if link(event['description']) is not None:
        return f" [{summary}]({link(event['description'])})" 
    else: return f" {summary}"

def endtime(start:datetime, end:datetime):
    if start == end or (start + datetime.timedelta(days=1)) == end:
        return None
    elif (start + datetime.timedelta(days=1)) > end:
        return string(end, '%H:%M')
    else:
        return string(end, '%d.%m.')

def time(event: dict):
    end = endtime(event['start'], event['end'])
    startday = string(event['start'], '%d.%m.')
    time = string(event['start'], '%H:%M')
    if time == end or end == None:
        if time == "00:00":
            return f"{startday}"
        return f"{startday} {time}:"
    else:
        if time == "00:00":
            return f"{startday} - {end}"
        elif event['start'] + datetime.timedelta(days=1) < event['end']:
            return f"{startday} - {end}"
        return f"{startday} {time}:"
    
def recurring(event:dict, message:str, mode:['plain','md','html']):
    regex = '\.\s.*'
    regex += re.escape(markdownify(f"{event['summary']}") if mode in ['md', 'html'] else f"\..*{event['summary']}")
    entry = re.search(regex, message)
    if entry is None:
        message += markdownify(time(event)) + markdown_title_link(event) if mode in ['md','html'] else time(event) + f" {event['summary']}"
        message += newline()
        return message
    else:
        index = message.find(entry.group())
        return message[:index+2] + f"& {markdownify(string(event['start'], '%d.%m.'))} " + message[index+2:]
        
    
def markdownify(text: str):
    """
    escape characters to use markdown
    """
    if text is None:
        return ""
    escape_chars = "?_–*[]()~`>#+-=|.!'{''}''"
    translate_dict = {c: "\\" + c for c in escape_chars}
    return text.translate(str.maketrans(translate_dict))
    
def message(events:dict, querystart: int, queryend: int, mode:['plain','md','html']):
    """
    
    """
    message = markdownify(header(querystart, queryend)) if mode in ['md','html'] else header(querystart, queryend)
    for calendar_name, event_list in events.items():
        if event_list == []:
            continue
        message += newline()
        message += emoji(calendar_name) + f"{markdownify(calendar_name)}" if mode in ['md','html'] else emoji(calendar_name) + calendar_name
        message += newline()
        for event in event_list:
            if event['recurrence'] is not None:
                message = recurring(event, message, mode)
            else:
                message += markdownify(time(event)) + markdown_title_link(event) if mode in ['md','html'] else time(event) + f" {event['summary']}"
                message += newline()
    message += newline()
    message += footer()
    return markdown.markdown(message.strip(), extensions=['nl2br']) if mode == 'html' else message.strip()
    
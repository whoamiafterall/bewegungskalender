import datetime
import pytz

# pytz helper function
def set_timezone(config:dict):
    global TIMEZONE
    TIMEZONE = pytz.timezone(config['format']['timezone']) # set time zone

# datetime helper functions
def today() -> datetime.date:
    return datetime.datetime.now().date()

def now(type: [str, datetime]):
    if type == str:
        return datetime.datetime.now().strftime("%d/%m/%Y %H:%M")
    if type == datetime:
        return datetime.datetime.now()

def to_datetime(date:str, config) -> datetime.datetime:
    "returns a datetime.datetime Object from a String using format specified in config."
    return datetime.datetime.strptime(date, config['mail']['input']['date_format'])

def to_timezone(dt:datetime.datetime) -> datetime.datetime:
    return dt.astimezone(TIMEZONE)

def fix_midnight(dt:datetime.datetime) -> datetime.datetime:
    if time(dt) == "(00:00)":
        return dt - datetime.timedelta(seconds=1)
    return dt

def days(delta) -> datetime.datetime:
    return datetime.timedelta(days=delta)

def check_datetime(date:datetime) -> datetime.date:
    return date if isinstance(date, datetime.datetime) else datetime.datetime.combine(date, datetime.datetime.min.time()).astimezone(TIMEZONE)
    
def date(day:datetime.date) -> str: # get date from a datetime object
    return day.strftime('%d.%m.')

def weekday(day:datetime.date) -> str: # get weekday from a datetime object
    return day.strftime('%a.')

def weekday_date(day:datetime.date) -> str:
    return weekday(day) + " " + date(day)

def time (datetime:datetime) -> str: # get time from a datetime object
    return datetime.strftime('(%H:%M)') 

def eventtime(start:datetime, end:datetime) -> str:
    print(start)
    print(end)
    if start == end or (start + datetime.timedelta(days=1)) == end:
        return f"{date(start)}" if time(start) == "(00:00)" else f"{date(start)} {time(start)}:"
    else:
        if time(start) == "(00:00)":
            return f"{date(start)} - {date(end)}"
        return f"{date(start)} - {date(end)}" if start + datetime.timedelta(days=1) < end else f"{date(start)} {time(start)}:"
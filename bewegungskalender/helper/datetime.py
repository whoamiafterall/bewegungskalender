from datetime import datetime, timedelta, date
import pytz

# pytz helper function
def set_timezone(config:dict):
    global TIMEZONE
    TIMEZONE = pytz.timezone(config['format']['timezone']) # set time zone

def to_datetime(date:str, config) -> datetime:
    "returns a datetime.datetime Object from a String using format specified in config."
    return datetime.strptime(date, config['form']['date_format'])

def fix_midnight(dt:datetime) -> datetime:
    if time(dt) == "(00:00)":
        return dt - timedelta(seconds=1)
    return dt

def check_datetime(date:date) -> datetime:
    return date if isinstance(date, datetime) else datetime.combine(date, datetime.min.time()).astimezone(TIMEZONE)
    
def date_str(day:datetime) -> str: # get date from a datetime object
    return day.strftime('%d.%m.')

def weekday(day:datetime) -> str: # get weekday from a datetime object
    return day.strftime('%a.')

def weekday_date(day:datetime) -> str:
    return weekday(day) + " " + date_str(day)

def time (datetime:datetime) -> str: # get time from a datetime object
    return datetime.strftime('(%H:%M)')
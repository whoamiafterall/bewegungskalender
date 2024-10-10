from _datetime import datetime, timedelta, date
from bewegungskalender.helper.config import CONFIG
import pytz

TIMEZONE = pytz.timezone(CONFIG['format']['timezone'])

def to_datetime(day:str, config) -> datetime:
    """returns a datetime.datetime Object from a String using format specified in config."""
    return datetime.strptime(day, config['form']['date_format'])

def fix_midnight(dt:datetime) -> timedelta|datetime:
    if time(dt) == "(00:00)":
        return dt - timedelta(seconds=1)
    return dt

def check_datetime(day:date) -> datetime:
    return day if isinstance(day, datetime) else datetime.combine(day, datetime.min.time()).astimezone(TIMEZONE)
    
def date_str(day:date) -> str: # get date from a datetime object
    return day.strftime('%d.%m.')

def weekday(day:date) -> str: # get weekday from a datetime object
    return day.strftime('%a.')

def weekday_date(day:date) -> str:
    return weekday(day) + " " + date_str(day)

def time (dt:datetime) -> str: # get time from a datetime object
    return dt.strftime('(%H:%M)')

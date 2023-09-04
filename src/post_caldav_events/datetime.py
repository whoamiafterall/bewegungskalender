import datetime
import pytz

# pytz helper function
def set_timezone(config:dict):
    global TIMEZONE
    TIMEZONE = pytz.timezone(config['format']['timezone']) # set time zone

# datetime helper functions
def today():
    return datetime.datetime.now().date()

def to_datetime(date:str, config) -> datetime.datetime:
    "returns a datetime.datetime Object from a String using format specified in config."
    return datetime.datetime.strptime(date, config['mail']['input']['date_format'])

def days(delta):
    return datetime.timedelta(days=delta)

def check_datetime(date:datetime):
    return date if isinstance(date, datetime.datetime) else datetime.datetime.combine(date, datetime.datetime.min.time()).astimezone(TIMEZONE)
    
def date(day:datetime.date): # get date from a datetime object
    return day.strftime('%d.%m.')

def weekday(day:datetime.date): # get weekday from a datetime object
    return day.strftime('%a.')

def time (datetime:datetime): # get time from a datetime object
    return datetime.astimezone(TIMEZONE).strftime('(%H:%M)') 

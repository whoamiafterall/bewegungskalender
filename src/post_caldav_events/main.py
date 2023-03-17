"""
main executable
"""

import argparse
import yaml
import datetime
import pytz
import caldav
import icalendar
from . import outputs


config = {}


def date_to_datetime(date):
    return datetime.datetime.combine(date,
             datetime.datetime.min.time()).astimezone(pytz.timezone(config['format']['timezone']))


def get_week_events(calendar, start_day, end_day):
    q_start_dt = date_to_datetime(start_day)
    q_end_dt = date_to_datetime(end_day)
    events = []
    try:
        for event in calendar.date_search(q_start_dt, q_end_dt):
            gevent = icalendar.Event.from_ical(event.data)
            for component in gevent.walk():
                if component.name == "VEVENT":
                    start_dt = component.get('dtstart').dt
                    try:
                        end_dt = component.get('dtend').dt
                        if not isinstance(end_dt, datetime.datetime):
                            end_dt = date_to_datetime(end_dt)
                        else:
                            end_dt = end_dt.astimezone(pytz.timezone(config['format']['timezone']))
                    except AttributeError:
                        end_dt = None
                    if not isinstance(start_dt, datetime.datetime):
                        start_dt = date_to_datetime(start_dt)
                        all_day = True
                    else:
                        start_dt = start_dt.astimezone(pytz.timezone(config['format']['timezone']))
                        if end_dt:
                            all_day = start_dt <= q_start_dt and end_dt >= q_end_dt
                        else:
                            all_day = start_dt <= q_start_dt
                    if all_day and end_dt == start_dt:
                        continue
                    if not start_dt < q_start_dt:
                        events.append({
                            'summary': component.get('summary'),
                            'location': component.get('location'),
                            'description': component.get('description'),
                            'start': start_dt,
                            'end': end_dt,
                            'all_day': all_day,
                            })
    except ConnectionError:
        print("Connection to Nextcloud failed.")
    sorted_events = []
    sorted_events += sorted([e for e in events], key=lambda d: d['start'])
    return sorted_events

def create_message_text(msg):
    if config['caldav']['current_day_override']:
        today = datetime.datetime.strptime(config['caldav']['current_day_override'], '%Y-%m-%d').date()
    else:
        today = datetime.datetime.now().date()
    start_day = today + datetime.timedelta(days=config['caldav']['offset_days'])
    end_day = start_day + datetime.timedelta(days=config['caldav']['range'])
    caldav_client = caldav.DAVClient(url=config['caldav']['url'], username=config['caldav']['username'], password=config['caldav']['password'])
    day_events = {}
    count = 0
    for caldavline in config['caldav']['calendars']:
        day = start_day + datetime.timedelta(days=count)
        count += 1
        calendar = caldav_client.calendar(url=caldavline['url'])
        calendar_name = calendar.get_properties([caldav.dav.DisplayName()])['{DAV:}displayname'] # type: ignore
        day_events[calendar_name] = get_week_events(calendar, start_day, end_day)
    msg.create(day_events, start_day, end_day)

def main(override_args = None):
    global config
    argparser = argparse.ArgumentParser(description='Post caldav events to telegram')
    argparser.add_argument('--config', dest='config_file', help='path to config file')
    argparser.add_argument('--get-telegram-updates', dest='get_telegram_updates', help='get telegram updates instead of posting events', action='store_true')
    argparser.set_defaults(config_file="config.yml", get_telegram_updates=False)
    if override_args is None:
        args = argparser.parse_args()
    else:
        args = argparser.parse_args(override_args)
    with open(args.config_file, 'r') as f:
        config = yaml.load(f, Loader=yaml.FullLoader)

    if args.get_telegram_updates:
        print(outputs.TelegramMarkdownv2Msg(config).get_updates())
        exit()

    if config['output']['type'] == 'telegram':
        Msg = outputs.TelegramMarkdownv2Msg
    elif config['output']['type'] == 'signal-cli':
        Msg = outputs.SignalCliMsg
    else:
        Msg = outputs.TextMsg

    msg = Msg(config)

    create_message_text(msg)

    if config['output']['stdout']:
        return msg.get_text()
    return msg.send()

if __name__ == '__main__':
    output = main()
    if output:
        print(output, end='')

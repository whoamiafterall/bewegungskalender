import locale
import pytz
import datetime
import re

class TextMsg:
    """
    basic and fallback to send text to stdout
    """

    def __init__(self, config):
        self.config = config
        self.msg = ""

    def create_space(self):
        self.msg += ("\n")


    def create_datetime_string(self, datetime_value, format):
        return datetime_value.astimezone(pytz.timezone(self.config['format']['timezone'])).strftime(format)

    def create_date(self, day):
        weekday = day.strftime('%a')
        date = day.strftime('%d\.%m')
        return weekday + " " + date

    def create_header(self, start_day, end_day):
        self.msg += f"📅 *Was passiert vom " + self.create_date(start_day) + " \- " + self.create_date(end_day) + "?*\n"

    def create_footer(self):
        self.msg += "🌐 *Links & Hinweise:*\n"
        self.msg += "\- [Monatsansicht öffnen](https://cloud.systemli.org/apps/calendar/p/zJsbBZJSQLCfkSsQ-gGA9ttt2T6PQgcKq-Brn9ook4EJWMx3ki-a7nAXkDxDETZJm58-df5QdyrBKa6H9Kpa-NpegYZLCqZjpxMa2-Rgk2wiaFQtLXGa5W-GeG6jNfCLSENW2Fs/dayGridMonth/now)\n"
        self.msg += "\- [Listenansicht öffnen](https://cloud.systemli.org/apps/calendar/p/zJsbBZJSQLCfkSsQ-gGA9ttt2T6PQgcKq-Brn9ook4EJWMx3ki-a7nAXkDxDETZJm58-df5QdyrBKa6H9Kpa-NpegYZLCqZjpxMa2-Rgk2wiaFQtLXGa5W-GeG6jNfCLSENW2Fs/listMonth/now)\n"
        self.msg += "\- [Mehr Infos, Legende & Termine eintragen](https://klimax.online/bewegungskalender)\n\n"

    def create_calendar_header(self, calendar_name):
        if calendar_name == 'Konferenzen & Treffen':
            self.msg += f"👥 "
        elif calendar_name == 'Aktionstage & Demos':
            self.msg += f"🟢 "
        elif calendar_name == 'Jahres & Gedenktage':
            self.msg += f"🟠 "
        elif calendar_name == 'System-Events & Termine':
            self.msg += f"🔴 "
        elif calendar_name == 'Camps & Festivals':
            self.msg += f"🔵 "
        elif calendar_name == 'Workshops & Skillshares':
            self.msg += f"🟣 "
        else:
            self.msg += f"🔍 "
        self.msg += f"{calendar_name} \n"

    def create_day_header(self, weekday, date):
        self.msg += "{weekday} - {date}"

    def create_event_header(self, summary, start_time=None, end_time=None, link=None):
        self.msg += f"{summary}  "
        if start_time:
            self.msg += f"{start_time} "
        if end_time:
            self.msg += f" - {end_time}"
        self.msg += "\n"

    def create_event_location(self, s):
        self.msg += f"🌍 {s}\n"

    def create_event_description(self, s):
        self.msg += f"🌐 {s}\n"

    def create_seperation(self):
        self.msg += "==================\n\n"

    def create_event(self, event):
        self.create_event_header(event)
        if event['location'] and self.config['format']['show_location']:
            self.create_event_location(event['location'])
        if event['description'] and self.config['format']['show_description']:
            description = event['description']
            cutoff = self.config['format']['cutoff_description']
            ellipsis = "[...]"
            if cutoff > 0 and len(description) > max(cutoff, len(ellipsis)):
                description = description[:cutoff-len(ellipsis)] + ellipsis
            self.create_event_description(description)

    def create_calendar_events(self, events):
    #    self.create_day_header(weekday, date)
        for event in events:
            self.create_event(event)

    def create(self, calendar_events, start_day, end_day):
        """
        currently, the events are sorted by time and into days with the same
        function which pulls them via caldav. for more flexibility regarding
        message layout more refactoring is necessary
        """
        locale.setlocale(locale.LC_TIME, self.config['format']['time_locale'])
        self.create_header(start_day, end_day)
        self.create_seperation()
        for calendar_name, events in calendar_events.items():
            if events:
                self.create_calendar_header(calendar_name)
                self.create_calendar_events(events)
                self.create_seperation()
        self.create_footer()
        self.finalize()

    def finalize(self):
        self.msg = self.msg.strip()

    def get_text(self):
        return self.msg

    def send(self):
        return(self.msg)


class TelegramMarkdownv2Msg(TextMsg):
    """
    send a message to a telegram channel formatted with telegram markdown v2
    """

    _bot = None

    def sanatize(self, text):
        """
        escape characters to use telegram markdown_v2 parse mode
        """
        if text is None:
            return ""
        escape_chars = "_*[]()~`>#+-=|{}.!"
        translate_dict = {c: "\\" + c for c in escape_chars}
        return text.translate(str.maketrans(translate_dict))

    @property
    def bot(self):
        if self._bot is None:
            import telegram
            self._bot = telegram.Bot(token=self.config['output']['token'])
        return self._bot

    def get_updates(self):
        """
        telegram helper method to retrieve group_id
        """
        updates = self.bot.get_updates()
        return "\n".join([str(u) for u in updates])

    def create_day_header(self):
        self.msg += f"*__{self.sanatize(weekday)}__ {self.sanatize(date)}*\n"

    def create_calendar_header(self, calendar_name):
        if calendar_name == 'Konferenzen & Treffen':
            self.msg += f"👥 "
        elif calendar_name == 'Aktionstage & Demos':
            self.msg += f"🟢 "
        elif calendar_name == 'Jahres & Gedenktage':
            self.msg += f"🟠 "
        elif calendar_name == 'System-Events & Termine':
            self.msg += f"🔴 "
        elif calendar_name == 'Camps & Festivals':
            self.msg += f"🔵 "
        elif calendar_name == 'Workshops & Skillshares':
            self.msg += f"🟣 "
        else:
            self.msg += f"🔍 "
        self.msg += f"*{self.sanatize(calendar_name)}* \n"

    def create_event_header(self, event):
        if not event['summary']:
            event['summary'] = "?"
        else:
            summary = event['summary']
        link = None
        if event['description'] != None:
            try:
                link = re.search("(?P<url>https?://[^\s]+)", event['description']).group("url")
            except AttributeError:
                link = None
        # Create end_time string with create_datetime_string
        if event['start'] == event['end'] or (event['start'] + datetime.timedelta(days=1)) == event['end']:
            end_time = None
        elif (event['start'] + datetime.timedelta(days=1)) > event['end']:
            end_time = self.create_datetime_string(event['end'], '\- %H:%M\)')
        else:
            end_time = self.create_datetime_string(event['end'], '\- %d\.%m')
        # Create start_time string with create_datetime_string
        start_day = self.create_datetime_string(event['start'], '%d\.%m')
        start_time = None
        if not event['all_day']:
            if not end_time == None:
                start_time = self.create_datetime_string(event['start'], '\(%H:%M')
            else:
                start_time = self.create_datetime_string(event['start'], '\(%H:%M\)')
        if start_time:
            self.msg += f"\- __{start_day}__{start_time}"
        if end_time:
            self.msg += f" {end_time}:"
        else:
            self.msg += f": "
        if link != None:
            self.msg += f" [{self.sanatize(summary)}]({link})"
        else:
            self.msg += f" {self.sanatize(summary)}"
        self.msg += "\n"

    def create_event_location(self, s):
        self.msg += f" _{self.sanatize(s)}_\n"

    def create_event_description(self, s):
        self.msg += f"_{self.sanatize(s)}_\n"

    def create_seperation(self):
        self.msg += "\n"

    def send(self):
        import telegram
        if len(self.msg) < 4096:
            self.bot.send_message(text=self.msg, chat_id=self.config['output']['group_id'], parse_mode=telegram.ParseMode.MARKDOWN_V2, disable_web_page_preview=True)
        else:
            print("Message too long for Telegram.")
            print (len(self.msg))
        return

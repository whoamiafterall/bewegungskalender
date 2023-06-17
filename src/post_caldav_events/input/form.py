from html.parser import HTMLParser
import imaplib
import email
import caldav
import icalendar
import datetime

def connect_imap(config: dict) -> imaplib.IMAP4_SSL:
    "returns an IMAP4_SSL-Client connected to server specified in config."
    try: imap = imaplib.IMAP4_SSL(config['input']['server'], config['input']['imap_port']); return imap
    except ConnectionError: return None

def get_davclient(config:dict) -> caldav.DAVClient:
    "returns a DAVClient connected to server specified in config."
    return caldav.DAVClient(url=config['caldav']['url'], username=config['caldav']['username'], password=config['caldav']['password']) 

def search_mails(imap: imaplib.IMAP4_SSL, config: dict) -> str:
    "returns a space-separated string sequence with uids of mails matching the mail account and subject specified in config."
    result, uids = imap.uid('search', None, 'FROM', config['input']['mail_from'], 'SUBJECT', config['input']['mail_subject'])
    return uids[0] if result == 'OK' else None

def fetch_mail(imap:imaplib.IMAP4_SSL, uid) -> email.message_from_bytes:
    "returns the payload(body) in html of an e-mail fetched by uid from IMAP4_SSL-Client"
    result, data = imap.uid('fetch', uid, '(RFC822)')
    return email.message_from_bytes(data[0][1]).get_payload() if result == 'OK' else None
        
def move_mail(imap: imaplib.IMAP4_SSL, uid, config):
    "copies an e-mail to another Inbox specified in config and marks it as seen. Deletes the first mail afterwards."
    imap.uid('store', uid, '+FLAGS', '\\Seen'); imap.uid('copy', uid, config['input']['move_to']); imap.uid('store', uid, '+FLAGS', '\\Deleted')

def to_datetime(date:str, config) -> datetime.datetime:
    "returns a datetime.datetime Object from a String using format specified in config."
    return datetime.datetime.strptime(date, config['input']['date_format'])

def update_events(config):
    imap = connect_imap(config)
    if imap == None: print('Connection to IMAP Server failed'); return None
    imap.login(config['input']['mail_account'], config['input']['password'])
    imap.select(config['input']['inbox'])
    uids = search_mails(imap, config)
    if uids is None: print("No matching form emails found."); return None
    try:
        davclient = get_davclient(config)
        calendar = davclient.calendar(url=config['input']['calendar'])
    except ConnectionError:
        print("Connection to Nextcloud failed."); return
    for uid in uids.split():
        parser = ParseWPForms()
        data = parser.parse(fetch_mail(imap, uid))
        print(data)
        move_mail(imap, uid, config)
        event = icalendar.Event()
        event.add('summary',data[0])
        event.add('dtstart',to_datetime(data[1], config))
        event.add('dtend',to_datetime(data[2], config))
        event.add('description',data[3])
        calendar.add_event(event.to_ical())
        parser.formdata.clear()
    imap.expunge(); imap.close(); imap.logout()

class ParseWPForms(HTMLParser):
    isformdata = bool; formdata = []
    def handle_data(self, data):
        if self.isformdata == True: self.formdata.append(data)

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]):
        if tag == "td": 
            for name, value in attrs: 
                if name == 'style': 
                    if value == "color:#555555;padding-top: 3px;padding-bottom: 20px;": self.isformdata = True

    def handle_endtag(self, tag: str) -> None:
        if tag == "td": self.isformdata = False

    def parse(self, data) -> list:
        self.feed(data); return self.formdata
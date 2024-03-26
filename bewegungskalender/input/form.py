from html.parser import HTMLParser
import imaplib
import email
import icalendar
import logging
from bewegungskalender.helper.datetime import to_datetime
from bewegungskalender.nextcloud.fetch import connect_davclient

def connect_imap(config: dict) -> imaplib.IMAP4_SSL:
    "returns an IMAP4_SSL-Client connected to server specified in config."
    try: imap = imaplib.IMAP4_SSL(config['mail']['server'], config['mail']['imap_port']); return imap
    except ConnectionError: 
        logging.exception('Could not connect to IMAP-Server...'); return None

def search_mails(imap: imaplib.IMAP4_SSL, config: dict) -> str:
    "returns a space-separated string sequence with uids of mails matching the mail account and subject specified in config."
    result, uids = imap.uid('search', None, 'FROM', config['mail']['sender'], 'SUBJECT', config['mail']['input']['subject'])
    return uids[0] if result == 'OK' else None

def fetch_mail(imap:imaplib.IMAP4_SSL, uid) -> email.message_from_bytes:
    "returns the payload(body) in html of an e-mail fetched by uid from IMAP4_SSL-Client"
    result, data = imap.uid('fetch', uid, '(RFC822)')
    return email.message_from_bytes(data[0][1]).get_payload() if result == 'OK' else None
        
def move_mail(imap: imaplib.IMAP4_SSL, uid, config):
    "copies an e-mail to another Inbox specified in config and marks it as seen. Deletes the first mail afterwards."
    imap.uid('store', uid, '+FLAGS', '\\Seen'); imap.uid('copy', uid, config['mail']['input']['move_to']); imap.uid('store', uid, '+FLAGS', '\\Deleted')

def print_data(data):
    "print data to stdout in a beautiful way, so it appears nicely in cron-mails"
    log = f"{data[0]} "
    log += f"{data[1]} "
    log += f"{data[2]} "
    log += f"{data[3]} "
    log += f"{data[4]} "
    log += f"{data[5]} "
    print(log)
    return

def compose_title(data):
    return f"{data[0]} ({data[3]})"

def update_events(config):
    logging.debug('Connecting to IMAP server...')
    imap = connect_imap(config)
    if imap == None: print('Connection to IMAP Server failed'); return None
    logging.debug('Logging into IMAP-Client with credentials...')
    imap.login(config['mail']['account'], config['mail']['password'])
    imap.select(config['mail']['input']['inbox'])
    logging.debug('Searching INBOX for matching e-mails...')
    uids = search_mails(imap, config)
    if uids is None: print("No matching form emails found."); return None
    try:
        logging.debug('Connecting to Nextcloud DAV Interface...')
        davclient = connect_davclient(config)
        calendar = davclient.calendar(url=config['mail']['input']['calendar'])
    except ConnectionError:
        logging.exception('Connection to Nextcloud failed.'); return
    logging.debug('Parsing E-Mails to Events...')
    for uid in uids.split():
        parser = ParseWPForms()
        data = parser.parse(fetch_mail(imap, uid))
        print_data(data)
        move_mail(imap, uid, config)
        event = icalendar.Event()
        event.add('summary', compose_title(data))
        event.add('dtstart',to_datetime(data[1], config))
        event.add('dtend',to_datetime(data[2], config))
        event.add('location', data[4])
        event.add('description',data[5])
        calendar.add_event(event.to_ical())
        parser.formdata.clear()
    logging.debug('Closing IMAP Connection...')
    imap.expunge(); imap.close(); imap.logout()

class ParseWPForms(HTMLParser):
    isformdata = bool; formdata = []
    def handle_data(self, data):
        if self.isformdata == True: self.formdata.append(data)

    def handle_starttag(self, tag: str, attrs: list):
        if tag == "td": 
            for name, value in attrs: 
                if name == 'style': 
                    if value == "color:#555555;padding-top: 3px;padding-bottom: 20px;": self.isformdata = True

    def handle_endtag(self, tag: str) -> None:
        if tag == "td": self.isformdata = False

    def parse(self, data) -> list:
        self.feed(data); return self.formdata
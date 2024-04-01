import imaplib
import email
from bewegungskalender.helper.parsing import ParseWPForms
import caldav
import icalendar
import logging
from bewegungskalender.helper.datetime import to_datetime

def connect_imap(config: dict) -> imaplib.IMAP4_SSL:
    logging.debug('Connecting to IMAP server using credential from config...')
    try: 
        imap = imaplib.IMAP4_SSL(config['mail']['server'], config['mail']['imap_port']) 
        imap.login(config['mail']['account'], config['mail']['password'])
        imap.select(config['mail']['input']['inbox'])
        return imap
    except ConnectionError: 
        logging.exception('Could not connect to IMAP-Server...'); 
        exit(code=1)

def update_events(config: dict, davclient: caldav.DAVClient):
    # Connect to IMAP Client
    imap = connect_imap(config)
    
    # Search for Mails that fit the given pattern in config
    sender = config['form']['sender']
    subject = config['form']['subject']
    logging.debug(f"Searching INBOX for e-mails from {sender} with subject {subject}...")
    result, uids = imap.uid('search', None, 'FROM', sender, 'SUBJECT', )
    if result != 'OK': # No Mails found, continue in main.py
        logging.info("No matching form emails found."); return None
    else: 
        logging.info(f"Found {len(uids)} matching E-Mails!")
        
        # Get Calendar from CalDAV-Server and Parser
        calendar = davclient.calendar(url=config['form']['calendar'])
        parser = ParseWPForms()
    
    # For each Mail that fits the given pattern
    for uid in uids[0].split():
        # Get the Body from the E-Mail
        result, data = imap.uid('fetch', uid, '(RFC822)')
        if result == 'OK': # Mail was found at given uid
            body = email.message_from_bytes(data[0][1]).get_payload() 
        else:
            logging.exception(f"Couldn't find the mail {uid} or get the payload from it.")
    
        # Get Parser and extract form Data from HTML to a list
        logging.debug(f"Parsing E-Mail {uid} to Event and adding it to Calendar...")
        data = parser.parse(body)
        
        # Create Event from data and add it to the calendar
        event = icalendar.Event()
        event.add('summary', f"{data[0]} ({data[3]})")
        event.add('dtstart',to_datetime(data[1], config))
        event.add('dtend',to_datetime(data[2], config))
        event.add('location', data[4])
        event.add('description',data[5])
        calendar.add_event(event.to_ical())
        logging.info(f"Successfully added {data[0]} ({data[3]}) to calendar!")
        parser.formdata.clear()
        
        # Move Mail to another Inbox
        logging.debug(f"Moving Mail {uid} to {config['form']['move_to']}...")
        imap.uid('store', uid, '+FLAGS', '\\Seen'); 
        imap.uid('copy', uid, config['form']['move_to']); 
        imap.uid('store', uid, '+FLAGS', '\\Deleted')
        
    logging.debug('Closing IMAP Connection...')
    imap.expunge(); imap.close(); imap.logout()

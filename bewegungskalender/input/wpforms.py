import imaplib
import email
from caldav import Calendar
from bewegungskalender.helper.parsing import ParseWPForms
from bewegungskalender.server.calDAV import connect_davclient
import icalendar
import logging
from bewegungskalender.helper.datetime import to_datetime

def connect_imap(config: dict) -> imaplib.IMAP4_SSL:
    logging.debug('Connecting to IMAP server using credential from config...')
    try: 
        imap = imaplib.IMAP4_SSL(config['mail']['server'], config['mail']['imap_port']) 
        imap.login(config['mail']['account'], config['mail']['password'])
        return imap
    except ConnectionError: 
        logging.exception('Could not connect to IMAP-Server...'); 
        exit(code=1)

def update_wpform(config: dict, calendar:Calendar):
    logging.info('Updating Events by scanning E-Mails from WPForms Lite...')
    # Connect to IMAP Client
    imap = connect_imap(config)
    imap.select(config['wpform']['inbox'])
    
    # Search for Mails that fit the given pattern in config
    sender = config['wpform']['sender']
    subject = config['wpform']['subject']
    logging.debug(f"Searching INBOX for e-mails from {sender} with subject {subject}...")
    result, uids = imap.uid('search', None, 'FROM', sender, 'SUBJECT', subject)
    if result != 'OK': # No Mails found, continue in main.py
        logging.info("No matching form emails found."); return None
    elif len(uids[0]) == 0: 
        logging.info(f"Found {len(uids[0])} matching E-Mails!"); return None
    else:
        logging.info(f"Found {len(uids[0])} matching E-Mails!")
        
        # Get Calendar from CalDAV-Server and Parser
        parser = ParseWPForms()
    mails:list = uids[0].split()
    # For each Mail that fits the given pattern
    for mail in mails:
        # Get the Body from the E-Mail
        result, data = imap.uid('fetch', mail, '(RFC822)')
        if result == 'OK': # Mail was found at given uid
            body = email.message_from_bytes(data[0][1]).get_payload() 
        else:
            logging.exception(f"Couldn't find the mail {mail} or get the payload from it.")
    
        # Get Parser and extract form Data from HTML to a list
        logging.debug(f"Parsing E-Mail {mail} to Event and adding it to Calendar...")
        data = parser.parse(body)
        
        # Create Event from data and add it to the calendar
        event = icalendar.Event()
        try:
            event.add('summary', f"{data[0]} ({data[3]})")
            try:
                event.add('dtstart',to_datetime(data[1], config))
                event.add('dtend',to_datetime(data[2], config))
            except ValueError:
                logging.exception(f"Es gibt bei {data[1]} oder {data[2]} ein Problem mit den Datumsangaben: {ValueError}")
            event.add('location', data[4])
            event.add('description',data[5])
        except IndexError:
             logging.exception(f"Es gibt bei {data} ein Problem, wahrscheinlich fehlt eine Angabe: {IndexError}")
        calendar.add_event(event.to_ical())
        logging.info(f"Successfully added {data[1]}: {data[0]} ({data[3]}) to calendar!")
        parser.formdata.clear()
        
        # Move Mail to another Inbox
        logging.debug(f"Moving Mail {mail} to {config['form']['move_to']}...")
        imap.uid('store', mail, '+FLAGS', '\\Seen'); 
        imap.uid('copy', mail, config['form']['move_to']); 
        imap.uid('store', mail, '+FLAGS', '\\Deleted')
        mails.remove(mail)
        
    logging.debug('Closing IMAP Connection...')
    imap.expunge(); imap.close(); imap.logout()
    logging.info('Finished updating Events from WPForms.')
import datetime
import smtplib, ssl, logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.utils import formatdate, make_msgid
from bewegungskalender.helper.formatting import Format
from bewegungskalender.output.message import message
from bewegungskalender.helper.datetime import date

def send_mail(config:dict, start:datetime.date, stop:datetime.date, events:dict, recipients:list[str], format:Format):
    server:str = config['mail']['server']
    port:str = config['mail']['smtp_port']
    logging.debug('Connecting to SMTP Server...')
    with smtplib.SMTP_SSL(server, port, context=ssl.create_default_context()) as smtp:
        smtp.ehlo()
        smtp.set_debuglevel(1)
        logging.debug('Logging into SMTP Client with credentials...')
        smtp.login(config['mail']['account'], config['mail']['password']) 
        mail = MIMEMultipart("alternative")
        mail.add_header('subject', f"{config['newsletter']['subject']} {date(start)} - {date(stop)}")
        mail.add_header('from', config['newsletter']['sender'])
        mail.add_header('date', formatdate(localtime=True))
        mail.add_header('Message-ID', make_msgid())
        mail.add_header('Return-Path', 'noreply-bewegungskalender@systemli.org')
        mail.attach(MIMEText(message(config, events, start, stop, format), "html"))
        if recipients is not None:
            for recipient in recipients:
                mail["to"] = recipient
                logging.debug(f"Sending E-Mail to {recipient}...")
                smtp.sendmail(config['newsletter']['sender'], recipient, mail.as_string())
        logging.debug('Quitting Connection to SMTP Server...')
        smtp.quit()
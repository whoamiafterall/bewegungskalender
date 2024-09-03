import datetime
import smtplib, ssl, logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.utils import formatdate, make_msgid
from bewegungskalender.helper.formatting import Format
from bewegungskalender.output.message import MultiFormatMessage
from bewegungskalender.helper.cli import mail_receiver
from bewegungskalender.helper.datetime import date

def send_mail(config:dict, message:MultiFormatMessage, start:datetime.date, stop:datetime.date):
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
        mail.attach(MIMEText(message.txt, "txt"))
        mail.attach(MIMEText(message.html, "html"))
        if mail_receiver is not None:
            receiver = mail_receiver
        else: 
            receiver = config['newsletter']['receiver']
        if receiver is not None:
            for address in receiver:
                mail["to"] = address
                logging.debug(f"Sending E-Mail to {address}...")
                smtp.ehlo()
                smtp.sendmail(config['newsletter']['sender'], address, mail.as_string())
        logging.debug('Quitting Connection to SMTP Server...')
        smtp.quit()
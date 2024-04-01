import smtplib, ssl, logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.utils import formatdate, make_msgid
from bewegungskalender.output.message import message
from bewegungskalender.helper.datetime import date

def send_mail(config:dict, query_start, query_end, events:dict, recipients, format):
    server = config['mail']['server']
    port = config['mail']['smtp_port']
    logging.debug('Connecting to SMTP Server...')
    with smtplib.SMTP_SSL(server, port, context=ssl.create_default_context()) as smtp:
        smtp.ehlo()
        smtp.set_debuglevel(1)
        logging.debug('Logging into SMTP Client with credentials...')
        smtp.login(config['mail']['acccount'], config['mail']['password']) 
        mail = MIMEMultipart("alternative")
        mail.add_header('subject', f"{config['newsletter']['subject']} {date(query_start)} - {date(query_end)}")
        mail.add_header('from', config['newsletter']['sender'])
        mail.add_header('date', formatdate(localtime=True))
        mail.add_header('Message-ID', make_msgid())
        mail.add_header('Return-Path', 'noreply-bewegungskalender@systemli.org')
        mail.attach(MIMEText(message(config, events, query_start, query_end, format), "html"))
        if recipients is not None:
            for recipient in recipients:
                mail["to"] = recipient
                logging.debug(f"Sending E-Mail to {recipient}...")
                smtp.sendmail(config['newsletter']['sender'], recipient, mail.as_string())
        logging.debug('Quitting Connection to SMTP Server...')
        smtp.quit()
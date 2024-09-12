import smtplib, ssl
from datetime import date
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.utils import formatdate, make_msgid
from bewegungskalender.helper.formatting import Format
from bewegungskalender.output.message import MultiFormatMessage
from bewegungskalender.helper.cli import MAIL_TO, START, END
from bewegungskalender.helper.logger import LOG
from bewegungskalender.helper.datetime import date_str

def send_mail(config:dict, message:MultiFormatMessage):
    server:str = config['mail']['server']
    port:str = config['mail']['smtp_port']
    LOG.debug('Connecting to SMTP Server...')
    with smtplib.SMTP_SSL(server, port, context=ssl.create_default_context()) as smtp:
        smtp.ehlo()
        smtp.set_debuglevel(1)
        LOG.debug('Logging into SMTP Client with credentials...')
        smtp.login(config['mail']['account'], config['mail']['password']) 
        mail = MIMEMultipart("alternative")
        subject = f"{config['newsletter']['subject']} {date_str(START)} - {date_str(END)}"
        mail.add_header('subject', subject)
        mail.add_header('from', config['newsletter']['sender'])
        mail.add_header('date', formatdate(localtime=True))
        mail.add_header('Message-ID', make_msgid())
        mail.add_header('Return-Path', 'noreply-bewegungskalender@systemli.org')
        mail.attach(MIMEText(message.txt, "txt"))
        mail.attach(MIMEText(message.html, "html"))

        # Set Receiver from command-line argument if specified - else from config       
        receiver = MAIL_TO if MAIL_TO is not None else config['newsletter']['receiver']
        if receiver is not None:
            for address in receiver:
                mail["to"] = address
                LOG.debug(f"Sending E-Mail to {address}...")
                smtp.ehlo()
                smtp.sendmail(config['newsletter']['sender'], address, mail.as_string())
        LOG.debug('Quitting Connection to SMTP Server...')
        smtp.quit()
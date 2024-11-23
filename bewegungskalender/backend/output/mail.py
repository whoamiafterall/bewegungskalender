import smtplib, ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.utils import formatdate, make_msgid
from bewegungskalender.backend.formatting.message import MultiFormatMessage
from bewegungskalender.backend.io.cli import MAIL_TO, START, END
from bewegungskalender.backend.io.config import MAIL_ACC, MAIL_PW, MAIL_SUBJECT, MAIL_SENDER, MAIL_RECEIVER, SMTP, MAIL_SRV
from bewegungskalender.libs.logger import LOGGER

def send_mail(message:MultiFormatMessage):
    LOGGER.debug('Connecting to SMTP Server...')
    with smtplib.SMTP_SSL(MAIL_SRV, SMTP, context=ssl.create_default_context()) as smtp:
        smtp.ehlo()
        smtp.set_debuglevel(1)
        LOGGER.debug('Logging into SMTP Client with credentials...')
        smtp.login(MAIL_ACC, MAIL_PW)
        mail = MIMEMultipart("alternative")
        subject = f"{MAIL_SUBJECT} {START:%d.%m.} - {END:%d.%m.}"
        mail.add_header('subject', subject)
        mail.add_header('from', MAIL_SENDER)
        mail.add_header('date', formatdate(localtime=True))
        mail.add_header('Message-ID', make_msgid())
        mail.add_header('Return-Path', 'noreply-bewegungskalender@systemli.org')
        mail.attach(MIMEText(message.txt, "txt"))
        mail.attach(MIMEText(message.html, "html"))

        # Set Receiver from command-line argument if specified - else from config       
        receiver:list = [MAIL_TO] if MAIL_TO is not None else MAIL_RECEIVER
        if receiver is not None:
            for address in receiver:
                mail["to"] = address
                LOGGER.debug(f"Sending E-Mail to {address}...")
                smtp.ehlo()
                smtp.sendmail(MAIL_SENDER, address, mail.as_string())
        LOGGER.debug('Quitting Connection to SMTP Server...')
        smtp.quit()
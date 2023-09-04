import smtplib, ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from post_caldav_events.output.message import message
from post_caldav_events.datetime import date

def send_newsletter(config:dict, query_start, query_end, events:dict, recipient):
    with smtplib.SMTP_SSL(config['mail']['server'], config['mail']['smtp_port'] , context=ssl.create_default_context()) as smtp:
        smtp.ehlo()
        smtp.login(config['mail']['account'], config['mail']['password']) 
        mail = MIMEMultipart("alternative")
        mail["Subject"] = f"{config['mail']['newsletter']['subject']} {date(query_start)} - {date(query_end)}"
        mail["From"] = config['mail']['sender']
        mail.attach(MIMEText(message(config, events, query_start, query_end, mode='html'), "html"))
        if recipient is None: #Taking E-Mail-Adresses specified in config file
            for recipient in config['mail']['newsletter']['recipients']:
                mail["To"] = recipient['mail']
                print(recipient['mail'])
                smtp.sendmail(config['mail']['sender'], recipient['mail'], mail.as_string())
        else: #Taking an E-Mail-Adress from cli-argument for testing
            mail["To"] = recipient
            smtp.sendmail(config['mail']['sender'], recipient, mail.as_string())
        smtp.quit()
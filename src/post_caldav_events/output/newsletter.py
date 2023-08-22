import smtplib, ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from post_caldav_events.output.message import date, message


def send_newsletter(config:dict, query_start, query_end, events:dict, recipient):
    with smtplib.SMTP_SSL(config['mail']['server'], config['mail']['smtp_port'] , context=ssl.create_default_context()) as smtp:
        smtp.ehlo()
        smtp.login(config['mail']['account'], config['mail']['password']) 
        mail = MIMEMultipart("alternative")
        mail["Subject"] = f"{config['mail']['newsletter']['subject']} {date(query_start)} - {date(query_end)}"
        mail["From"] = config['mail']['sender']
        mail.attach(MIMEText(message(events, query_start, query_end, mode='html'), "html"))
        if recipient is None:
            for recipient in config['mail']['newsletter']['recipients']:
                mail["To"] = recipient['mail']
                smtp.sendmail(config['mail']['sender'], recipient['mail'], mail.as_string())
        else:
            mail["To"] = recipient
            smtp.sendmail(config['mail']['sender'], recipient, mail.as_string())
        smtp.quit()
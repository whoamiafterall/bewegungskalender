import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# E-Mail-Parameter
sender_email = "sender@example.com"
sender_password = "password"
receiver_emails = ["receiver1@example.com", "receiver2@example.com"]
subject = "Test-E-Mail"
body = "Dies ist eine Test-E-Mail von Python."

# E-Mail-Objekt erstellen
message = MIMEMultipart()
message["From"] = sender_email
message["To"] = ", ".join(receiver_emails)
message["Subject"] = subject
message.attach(MIMEText(body, "plain"))

# SMTP-Server-Verbindung herstellen
smtp_server = smtplib.SMTP("smtp.gmail.com", 587)
smtp_server.starttls()
smtp_server.login(sender_email, sender_password)

# E-Mail senden
smtp_server.sendmail(sender_email, receiver_emails, message.as_string())
smtp_server.quit()
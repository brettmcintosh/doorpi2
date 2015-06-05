import smtplib
from datetime import datetime
from email.mime.text import MIMEText

from alarm import settings


class EmailNotification(object):

    def __init__(self, message):
        self.message = message
        self.smtp_server = None
        self.smtp_response = None
        self.connect_to_server()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.smtp_server.quit()

    def connect_to_server(self):
        # connect and log in to smtp server
        smtp = smtplib.SMTP(settings.EMAIL_SERVER_URL, settings.EMAIL_SERVER_PORT, timeout=10)
        smtp.starttls()
        smtp.ehlo_or_helo_if_needed()
        self.smtp_response = smtp.login(settings.EMAIL_USERNAME, settings.EMAIL_PASSWORD)
        self.smtp_server = smtp

    def send(self):
        # create message
        msg = MIMEText(self.message)
        msg['Subject'] = 'DoorPi'
        msg['From'] = settings.EMAIL_USERNAME
        msg['To'] = ', '.join(settings.EMAIL_RECIPIENTS)

        # send message
        self.smtp_server.send_message(msg)


def create_email_message(sensor_name):
    msg = settings.EMAIL_MESSAGE
    timestamp = datetime.now().strftime(settings.EMAIL_TIME_FORMAT)
    msg = msg.replace('<time>', timestamp).replace('<sensor>', sensor_name)
    return msg
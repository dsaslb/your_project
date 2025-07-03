import os, smtplib
from email.mime.text import MIMEText

def send_email(subject, body):
    host = os.environ.get('EMAIL_HOST')
    port = int(os.environ.get('EMAIL_PORT', 587))
    user = os.environ.get('EMAIL_USER')
    pw = os.environ.get('EMAIL_PASS')
    to = os.environ.get('EMAIL_TO', user)
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = user
    msg['To'] = to
    with smtplib.SMTP(host, port) as server:
        server.starttls()
        server.login(user, pw)
        server.sendmail(user, [to], msg.as_string())

if __name__ == '__main__':
    import sys
    send_email(sys.argv[1], sys.argv[2]) 
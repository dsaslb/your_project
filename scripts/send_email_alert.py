import os, smtplib
from email.mime.text import MIMEText
from typing import Optional

def send_email(subject: str, body: str) -> None:
    host: Optional[str] = os.environ.get('EMAIL_HOST')
    port: int = int(os.environ.get('EMAIL_PORT', 587))
    user: Optional[str] = os.environ.get('EMAIL_USER')
    pw: Optional[str] = os.environ.get('EMAIL_PASS')
    to: str = os.environ.get('EMAIL_TO', user or "")
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = user or ""
    msg['To'] = to
    with smtplib.SMTP(host or "", port) as server:
        server.starttls()
        server.login(user or "", pw or "")
        server.sendmail(user or "", [to], msg.as_string())

if __name__ == '__main__':
    import sys
    send_email(sys.argv[1], sys.argv[2]) 
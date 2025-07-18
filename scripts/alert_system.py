import smtplib
import requests
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import json
from datetime import datetime


class AlertSystem:
    def __init__(self, config):
        self.config = config
        self.smtp_server = config.get("smtp_server", "smtp.gmail.com")
        self.smtp_port = config.get("smtp_port", 587)
        self.email = config.get("email")
        self.password = config.get("password")
        self.webhook_url = config.get("webhook_url")

    def send_email_alert(self, subject, message):
        """?대찓???뚮┝ 諛쒖넚"""
        if not self.email or not self.password:
            return False

        try:
            msg = MIMEMultipart()
            msg["From"] = self.email
            msg["To"] = self.email
            msg["Subject"] = f"[Your Program Alert] {subject}"

            msg.attach(MIMEText(message, "plain"))

            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.email, self.password)
            server.send_message(msg)
            server.quit()

            return True
        except Exception as e:
            print(f"Email alert failed: {e}")
            return False

    def send_webhook_alert(self, message):
        """?뱁썒 ?뚮┝ 諛쒖넚"""
        if not self.webhook_url:
            return False

        try:
            payload = {
                "text": f"[Your Program Alert] {message}",
                "timestamp": datetime.now().isoformat(),
            }

            response = requests.post(self.webhook_url, json=payload, timeout=10)
            return response.status_code == 200
        except Exception as e:
            print(f"Webhook alert failed: {e}")
            return False

    def send_alert(self, subject, message, alert_type="both"):
        """?뚮┝ 諛쒖넚"""
        success = True

        if alert_type in ["email", "both"]:
            success &= self.send_email_alert(subject, message)

        if alert_type in ["webhook", "both"]:
            success &= self.send_webhook_alert(message)

        return success


# ?ㅼ젙 ?덉떆
config = {
    "smtp_server": "smtp.gmail.com",
    "smtp_port": 587,
    "email": "your-email@gmail.com",
    "password": "your-app-password",
    "webhook_url": "https://hooks.slack.com/services/YOUR/WEBHOOK/URL",
}

alert_system = AlertSystem(config)

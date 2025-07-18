#!/usr/bin/env python3
"""
외부 연동(슬랙/이메일/웹훅) 알림/자동화 함수 샘플
- 장애/이상/보안 이벤트 발생 시 실시간 알림 전송
- 초보자/운영자 안내 주석 포함

사용법:
python scripts/notify_external.py --type slack --message "테스트 알림"
"""
import argparse
import requests
import smtplib
from email.mime.text import MIMEText

def send_slack_alert(webhook_url, message):
    payload = {"text": message}
    resp = requests.post(webhook_url, json=payload)
    print(f"[슬랙] 응답: {resp.status_code}")

def send_email_alert(smtp_server, from_addr, to_addr, subject, message):
    msg = MIMEText(message)
    msg['Subject'] = subject
    msg['From'] = from_addr
    msg['To'] = to_addr
    with smtplib.SMTP(smtp_server) as server:
        server.sendmail(from_addr, [to_addr], msg.as_string())
    print(f"[이메일] {to_addr}로 전송 완료")

def send_webhook_alert(webhook_url, message):
    resp = requests.post(webhook_url, json={"alert": message})
    print(f"[웹훅] 응답: {resp.status_code}")

def main():
    parser = argparse.ArgumentParser(description='외부 연동 알림 테스트')
    parser.add_argument('--type', required=True, choices=['slack', 'email', 'webhook'], help='알림 타입')
    parser.add_argument('--message', required=True, help='알림 메시지')
    args = parser.parse_args()
    if args.type == 'slack':
        webhook_url = 'https://hooks.slack.com/services/your/webhook/url'  # 실제 값으로 교체
        send_slack_alert(webhook_url, args.message)
    elif args.type == 'email':
        smtp_server = 'localhost'  # 실제 SMTP 서버 주소로 교체
        from_addr = 'noreply@your_program.com'
        to_addr = 'admin@your_program.com'
        subject = '[알림] 시스템 이벤트'
        send_email_alert(smtp_server, from_addr, to_addr, subject, args.message)
    elif args.type == 'webhook':
        webhook_url = 'https://your-webhook-endpoint'  # 실제 값으로 교체
        send_webhook_alert(webhook_url, args.message)

if __name__ == '__main__':
    main() 
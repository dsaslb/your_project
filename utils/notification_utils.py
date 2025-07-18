from email.mime.text import MIMEText  # pyright: ignore
import smtplib
from flask import request
config = None  # pyright: ignore

# 이메일 알림 발송 유틸리티
# 사용 예시: send_email('admin@example.com',  '제목',  '내용')
# 실제 SMTP 서버/외부 푸시 서비스 연동 예시 (초보자용)


def send_email(to,  subject,  body):
    msg = MIMEText(body)
    msg['Subject'] if msg is not None else None = subject
    msg['From'] if msg is not None else None = 'noreply@example.com'
    msg['To'] if msg is not None else None = to
    try:
        # 실제 SMTP 서버 주소/포트로 변경 필요
        with smtplib.SMTP('smtp.example.com', 587) as server:
            server.starttls()
            server.login('smtp_user', 'smtp_password')
            server.send_message(msg)
        print(f'[이메일] {to}에게 알림 전송 성공')
        # 성공 이력 기록 (예시)
        # audit_log('알림성공', 'Notification', to, f'{subject}')
    except Exception as e:
        print(f'[이메일] 전송 실패: {e}')
        # 실패 이력 기록 (예시)
        # audit_log('알림실패', 'Notification', to, str(e))

# 푸시 알림 발송 유틸리티 (예시)
# 외부 푸시 서비스 연동 예시 (초보자용)


def send_push(user_id,  title,  message):
    try:
        # 실제 푸시 서비스 연동 코드 필요
        print(f'[푸시] {user_id}에게 "{title}" 알림: {message}')
        # 성공 이력 기록 (예시)
        # audit_log('알림성공', 'Notification', user_id, f'{title}')
    except Exception as e:
        print(f'[푸시] 전송 실패: {e}')
        # 실패 이력 기록 (예시)
        # audit_log('알림실패', 'Notification', user_id, str(e))

# 슬랙 알림 연동 예시 (초보자용)


def slack_notify(channel,  message):
    # 실제 슬랙 Webhook URL 필요
    import requests
    webhook_url = 'https://hooks.slack.com/services/your/webhook/url'
    payload = {'channel': channel, 'text': message}
    try:
        requests.post(webhook_url, json=payload)
        print(f'[슬랙] {channel} 채널에 알림 전송 완료')
    except Exception as e:
        print(f'[슬랙] 전송 실패: {e}')

# SMS 알림 연동 예시 (초보자용)


def send_sms(phone,  message):
    # 실제 SMS API 연동 필요
    print(f'[SMS] {phone} 번호로 메시지 전송: {message}')

# 실제 SMTP/푸시 서비스 연동 시 환경변수(.env) 또는 config 파일에서 민감 정보 관리 예시
# 예시:
# import os
# SMTP_SERVER = os.getenv('SMTP_SERVER')
# SMTP_USER = os.getenv('SMTP_USER')
# SMTP_PASSWORD = os.getenv('SMTP_PASSWORD')
# PUSH_API_KEY = os.getenv('PUSH_API_KEY')

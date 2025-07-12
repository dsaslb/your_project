import requests
import os
import smtplib
from email.mime.text import MIMEText
from email.utils import formataddr
import time

def send_slack_alert(message: str, webhook_url: str = None):  # pyright: ignore
    if webhook_url is None:
        webhook_url = os.environ.get('SLACK_WEBHOOK_URL') or ""
    if not webhook_url:
        print('Slack Webhook URL이 설정되어 있지 않습니다.')
        return False
    payload = {"text": message}
    try:
        response = requests.post(webhook_url, json=payload)
        return response.status_code == 200
    except Exception as e:
        print(f"Slack 알림 전송 실패: {e}")
        return False

def send_email_alert(subject: str, message: str, to_email: str = ""):  # pyright: ignore
    smtp_server = os.environ.get('ALERT_SMTP_SERVER')
    smtp_port = int(os.environ.get('ALERT_SMTP_PORT', 587))
    smtp_user = os.environ.get('ALERT_SMTP_USER')
    smtp_pass = os.environ.get('ALERT_SMTP_PASS')
    from_email = os.environ.get('ALERT_FROM_EMAIL', smtp_user)
    if to_email is None:
        to_email = os.environ.get('ALERT_TO_EMAIL')
    if not (smtp_server and smtp_user and smtp_pass and to_email):
        print('이메일 알림 환경변수가 누락되었습니다.')
        return False
    
    try:
        msg = MIMEText(message, 'plain', 'utf-8')
        # formataddr의 두 번째 인자는 str이어야 하므로 None일 경우 빈 문자열로 대체합니다.
        msg['From'] = formataddr(('Alert System', from_email or ""))  # pyright: ignore
        msg['To'] = to_email
        msg['Subject'] = subject
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(smtp_user, smtp_pass)
            # from_email이 None일 수 있으므로 빈 문자열로 대체하여 타입 오류를 방지합니다.
            server.sendmail(from_email or "", [to_email], msg.as_string())  # pyright: ignore
            return True
    except Exception as e:
        print(f"이메일 알림 전송 실패: {e}")
        return False

def send_sms_alert(message: str, to_number: str = None):  # pyright: ignore
    """Twilio SMS 알림 전송"""
    # Twilio 환경변수 필요
    account_sid = os.environ.get('TWILIO_ACCOUNT_SID')
    auth_token = os.environ.get('TWILIO_AUTH_TOKEN')
    from_number = os.environ.get('TWILIO_FROM_NUMBER')
    if to_number is None:
        to_number = os.environ.get('TWILIO_TO_NUMBER') or ""  # pyright: ignore
    if not (account_sid and auth_token and from_number and to_number):
        print('SMS 알림 환경변수가 누락되었습니다.')
        return False
    try:
        url = f'https://api.twilio.com/2010-04-01/Accounts/{account_sid}/Messages.json'
        data = {
            'From': from_number,
            'To': to_number,
            'Body': message
        }
        response = requests.post(url, data=data, auth=(account_sid, auth_token))
        return response.status_code == 201
    except Exception as e:
        print(f"SMS 알림 전송 실패: {e}")
        return False

def send_kakao_alert(message: str, template_id: str = None):  # pyright: ignore
    """카카오톡 알림 전송"""
    access_token = os.environ.get('KAKAO_ACCESS_TOKEN')
    # template_id가 None일 수 있으므로, 환경변수에서 가져온 값이 None일 경우 빈 문자열로 대체합니다.
    template_id = template_id or os.environ.get('KAKAO_TEMPLATE_ID') or ""  # pyright: ignore
    to_number = os.environ.get('KAKAO_TO_NUMBER') or ""  # pyright: ignore
    
    if not (access_token and template_id and to_number):
        print('카카오톡 알림 환경변수가 누락되었습니다.')
        return False
    
    try:
        url = 'https://kakaoapi.aligo.in/akv10/template/'
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
        data = {
            'tpl_code': template_id,
            'receiver': to_number,
            'message': message
        }
        response = requests.post(url, json=data, headers=headers)
        return response.status_code == 200
    except Exception as e:
        print(f"카카오톡 알림 전송 실패: {e}")
        return False

def send_korean_sms_alert(message: str, to_number: str = None):  # pyright: ignore
    """국내 SMS 서비스 알림 전송 (네이버 클라우드 SMS)"""
    service_id = os.environ.get('NAVER_SMS_SERVICE_ID')
    access_key = os.environ.get('NAVER_SMS_ACCESS_KEY')
    secret_key = os.environ.get('NAVER_SMS_SECRET_KEY')
    from_number = os.environ.get('NAVER_SMS_FROM_NUMBER')
    if to_number is None:
        to_number = os.environ.get('NAVER_SMS_TO_NUMBER') or ""  # pyright: ignore
    
    if not (service_id and access_key and secret_key and from_number and to_number):
        print('네이버 SMS 알림 환경변수가 누락되었습니다.')
        return False
    
    try:
        url = f'https://sens.apigw.ntruss.com/sms/v2/services/{service_id}/messages'
        headers = {
            'Content-Type': 'application/json',
            'x-ncp-apigw-timestamp': str(int(time.time() * 1000)),
            'x-ncp-iam-access-key': access_key,
            'x-ncp-apigw-signature-v2': generate_signature(secret_key, 'POST', '/sms/v2/services/' + service_id + '/messages')
        }
        data = {
            'type': 'SMS',
            'from': from_number,
            'content': message,
            'messages': [{'to': to_number}]
        }
        response = requests.post(url, json=data, headers=headers)
        return response.status_code == 202
    except Exception as e:
        print(f"네이버 SMS 알림 전송 실패: {e}")
        return False

def send_alert(message: str, level: str = 'info', subject: str = ""):  # pyright: ignore
    """
    level: 'info', 'warning', 'critical'
    subject: 이메일 제목 (없으면 message 앞부분)
    """
    # Slack은 항상 전송
    send_slack_alert(f'[{level.upper()}] {message}')
    
    # 이메일/SMS는 warning/critical만 전송
    if level in ('warning', 'critical'):
        email_subject = subject or f'[{level.upper()}] 시스템 알림'
        send_email_alert(email_subject, message)
    
    # 카카오톡은 critical만 전송
    if level == 'critical':
        send_kakao_alert(f'[CRITICAL] {message}')
        send_korean_sms_alert(f'[CRITICAL] {message}')

def generate_signature(secret_key: str, method: str, url: str) -> str:
    """네이버 클라우드 API 서명 생성"""
    import hmac
    import hashlib
    import base64
    
    timestamp = str(int(time.time() * 1000))
    message = method + ' ' + url + '\n' + timestamp + '\n' + secret_key
    signature = base64.b64encode(hmac.new(secret_key.encode(), message.encode(), hashlib.sha256).digest())
    return signature.decode() 
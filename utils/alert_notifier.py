from typing import Optional, Dict, Any
import time
from email.utils import formataddr  # pyright: ignore
from email.mime.text import MIMEText  # pyright: ignore
import smtplib
import os
import requests
form = None  # pyright: ignore
environ = None  # pyright: ignore


# 슬랙/이메일 알림 연동 함수 예시
import requests
import smtplib
from email.mime.text import MIMEText

def send_slack_alert(message, webhook_url):
    payload = {"text": message}
    response = requests.post(webhook_url, json=payload)
    return response.status_code == 200

def send_email_alert(subject, content, to_email):
    # (이메일 전송 로직은 auto_report.py 참고)
    pass

if __name__ == "__main__":
    # 샘플: 슬랙 알림 전송
    webhook = "https://hooks.slack.com/services/xxx/yyy/zzz"
    send_slack_alert("🚨 시스템 이상 감지! 즉시 확인 필요.", webhook)


def send_sms_alert(message: str, to_number=None):  # pyright: ignore
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


def send_kakao_alert(message: str, template_id=None):  # pyright: ignore
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


def send_korean_sms_alert(message: str, to_number=None):  # pyright: ignore
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


def send_alert(message: str, level='info', subject=""):  # pyright: ignore
    """
    level: 'info', 'warning', 'critical'
    subject: 이메일 제목 (없으면 message 앞부분)
    """
    # Slack은 항상 전송
    send_slack_alert(f'[{level.upper()}] {message}')

    # 이메일/SMS는 warning/critical만 전송
    if level in ('warning', 'critical'):
        email_subject = subject or f'[{level.upper()}] 시스템 알림'
        send_email_alert(email_subject,  message)

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

class AlertNotifier:
    """알림 관리 클래스"""
    
    def __init__(self):
        self.settings = {
            'email_enabled': False,
            'slack_enabled': False,
            'webhook_enabled': False,
            'email': '',
            'slack_webhook': '',
            'critical_enabled': True,
            'warning_enabled': True,
            'info_enabled': False,
            'repeat_interval': 30
        }
        self.stats = {
            'total_sent': 0,
            'email_sent': 0,
            'slack_sent': 0,
            'webhook_sent': 0,
            'errors': 0
        }
        self.channel_status = {
            'email': {'status': 'unknown', 'last_test': None},
            'slack': {'status': 'unknown', 'last_test': None},
            'webhook': {'status': 'unknown', 'last_test': None}
        }
    
    @classmethod
    def get_settings(cls) -> Dict[str, Any]:
        """알림 설정 조회"""
        # 실제로는 데이터베이스나 설정 파일에서 조회
        return {
            'email_enabled': False,
            'slack_enabled': False,
            'webhook_enabled': False,
            'email': '',
            'slack_webhook': '',
            'critical_enabled': True,
            'warning_enabled': True,
            'info_enabled': False,
            'repeat_interval': 30
        }
    
    @classmethod
    def update_settings(cls, settings: Dict[str, Any]):
        """알림 설정 업데이트"""
        # 실제로는 데이터베이스나 설정 파일에 저장
        print(f"알림 설정 업데이트: {settings}")
    
    @classmethod
    def get_channel_status(cls) -> Dict[str, Any]:
        """알림 채널 상태 조회"""
        return {
            'email': {'status': 'unknown', 'last_test': None},
            'slack': {'status': 'unknown', 'last_test': None},
            'webhook': {'status': 'unknown', 'last_test': None}
        }
    
    @classmethod
    def get_notification_stats(cls) -> Dict[str, Any]:
        """알림 통계 조회"""
        return {
            'total_sent': 0,
            'email_sent': 0,
            'slack_sent': 0,
            'webhook_sent': 0,
            'errors': 0,
            'last_24h': 0
        }

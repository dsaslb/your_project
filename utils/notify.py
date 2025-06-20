import smtplib
import requests
import json
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from extensions import db
from models import User, ActionLog, Attendance
from utils.logger import log_action

class NotificationService:
    """알림 서비스 클래스"""
    
    def __init__(self):
        self.email_config = {
            'smtp_server': 'smtp.gmail.com',
            'smtp_port': 587,
            'username': 'your-email@gmail.com',
            'password': 'your-app-password'
        }
        
        self.kakao_config = {
            'api_url': 'https://kapi.kakao.com/v2/api/talk/memo/default/send',
            'access_token': 'your-kakao-access-token'
        }
    
    def send_email(self, to_email, subject, message, html_content=None):
        """이메일 발송"""
        try:
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = self.email_config['username']
            msg['To'] = to_email
            
            # 텍스트 버전
            text_part = MIMEText(message, 'plain', 'utf-8')
            msg.attach(text_part)
            
            # HTML 버전 (있는 경우)
            if html_content:
                html_part = MIMEText(html_content, 'html', 'utf-8')
                msg.attach(html_part)
            
            # SMTP 서버 연결 및 발송
            server = smtplib.SMTP(self.email_config['smtp_server'], self.email_config['smtp_port'])
            server.starttls()
            server.login(self.email_config['username'], self.email_config['password'])
            server.send_message(msg)
            server.quit()
            
            return True, "이메일 발송 성공"
            
        except Exception as e:
            return False, f"이메일 발송 실패: {str(e)}"
    
    def send_kakao_message(self, user_id, message):
        """카카오톡 메시지 발송"""
        try:
            headers = {
                'Authorization': f'Bearer {self.kakao_config["access_token"]}'
            }
            
            data = {
                'template_object': json.dumps({
                    'object_type': 'text',
                    'text': message,
                    'link': {
                        'web_url': 'https://your-restaurant-app.com',
                        'mobile_web_url': 'https://your-restaurant-app.com'
                    }
                })
            }
            
            response = requests.post(
                self.kakao_config['api_url'],
                headers=headers,
                data=data
            )
            
            if response.status_code == 200:
                return True, "카카오톡 발송 성공"
            else:
                return False, f"카카오톡 발송 실패: {response.text}"
                
        except Exception as e:
            return False, f"카카오톡 발송 실패: {str(e)}"
    
    def send_sms(self, phone_number, message):
        """SMS 발송 (가상)"""
        try:
            # 실제 SMS API 연동 시 여기에 구현
            # 예: 네이버 클라우드 플랫폼, 가비아 등
            print(f"[SMS] {phone_number}: {message}")
            return True, "SMS 발송 성공 (가상)"
            
        except Exception as e:
            return False, f"SMS 발송 실패: {str(e)}"

def send_notification(user, message, method='all'):
    try:
        print(f"[알림] to {user.name or user.username} ({getattr(user, 'phone', '-')}) : {message}")
        # 실제 API 연동은 아래 주석 해제 후 API 키 입력
        # api_url = "https://api-alimtalk.example.com/send"
        # payload = {...}
        # headers = {"Authorization": "Bearer YOUR_KAKAO_API_TOKEN"}
        # r = requests.post(api_url, json=payload, headers=headers)
        # if r.status_code == 200:
        #     print("카카오톡 알림 발송 성공")
        #     return True
        # else:
        #     print("알림 발송 실패:", r.text)
        #     return False
        return True
    except Exception as e:
        print("알림 예외:", e)
        return True

def send_email(user, subject, message):
    try:
        print(f"[이메일] to {getattr(user, 'email', '-')}: {subject} - {message}")
        # 실제 SMTP 연동은 아래 주석 해제
        # ...
        return True
    except Exception as e:
        print("이메일 예외:", e)
        return True

def send_sms(user, message):
    try:
        print(f"[SMS] to {getattr(user, 'phone', '-')}: {message}")
        # 실제 SMS 연동은 아래 주석 해제
        # ...
        return True
    except Exception as e:
        print("SMS 예외:", e)
        return True

def notify_salary_payment(user, amount, year, month):
    """급여 지급 알림"""
    message = f"""
{user.name or user.username}님,

{year}년 {month}월 급여가 지급되었습니다.

지급 금액: {amount:,}원
지급 일시: {datetime.now().strftime('%Y년 %m월 %d일 %H:%M')}

문의사항이 있으시면 관리자에게 연락해 주세요.

감사합니다.
레스토랑 관리 시스템
    """.strip()
    
    # 이메일 알림
    if user.email:
        send_notification(user, message, 'email')
    
    # SMS 알림 (선택사항)
    if user.phone:
        sms_message = f"{year}년{month}월 급여 {amount:,}원이 입금되었습니다."
        send_notification(user, sms_message, 'sms')

def notify_attendance_issue(user, year, month, lateness, early_leave, night_work):
    """근태 이상 알림"""
    issues = []
    if lateness > 0:
        issues.append(f"지각 {lateness}회")
    if early_leave > 0:
        issues.append(f"조퇴 {early_leave}회")
    if night_work > 0:
        issues.append(f"야근 {night_work}회")
    
    if issues:
        message = f"""
{user.name or user.username}님,

{year}년 {month}월 근태 현황을 알려드립니다.

발생 이슈: {', '.join(issues)}

근태 개선을 위해 노력해 주시기 바랍니다.

감사합니다.
레스토랑 관리 시스템
        """.strip()
        
        send_notification(user, message, 'email')

def notify_approval_result(user, approved):
    """승인 결과 알림"""
    if approved:
        message = f"""
{user.name or user.username}님,

회원가입이 승인되었습니다!

이제 시스템에 로그인하여 사용하실 수 있습니다.
로그인: https://your-restaurant-app.com/login

감사합니다.
레스토랑 관리 시스템
        """.strip()
    else:
        message = f"""
{user.name or user.username}님,

회원가입 신청이 거절되었습니다.

자세한 사유는 관리자에게 문의해 주세요.

감사합니다.
레스토랑 관리 시스템
        """.strip()
    
    send_notification(user, message, 'email')

def notify_system_maintenance(message, users=None):
    """시스템 점검 알림"""
    if users is None:
        users = User.query.filter_by(status='approved').all()
    
    for user in users:
        send_notification(user, message, 'email')

def notify_holiday_reminder(user, holiday_date, holiday_name):
    """공휴일 알림"""
    message = f"""
{user.name or user.username}님,

다음 공휴일을 안내드립니다.

공휴일: {holiday_date}
공휴명: {holiday_name}

공휴일 근무가 필요한 경우 미리 알려주세요.

감사합니다.
레스토랑 관리 시스템
    """.strip()
    
    send_notification(user, message, 'email')

def notify_birthday(user):
    """생일 축하 알림"""
    message = f"""
{user.name or user.username}님,

생일을 축하드립니다! 🎉

오늘 하루도 즐겁게 보내세요.
레스토랑에서 함께 일할 수 있어서 기쁩니다.

감사합니다.
레스토랑 관리 시스템
    """.strip()
    
    send_notification(user, message, 'email')

def log_notification(user_id, notification_type, message, success, error_msg=""):
    """알림 로그 기록"""
    try:
        action_log = ActionLog(
            user_id=user_id,
            action=f"NOTIFICATION_{notification_type.upper()}",
            message=f"{'성공' if success else '실패'}: {message[:100]}{'...' if len(message) > 100 else ''} {error_msg}"
        )
        db.session.add(action_log)
        db.session.commit()
    except Exception as e:
        print(f"알림 로그 기록 실패: {e}")

# 글로벌 알림 서비스 인스턴스
notification_service = NotificationService() 
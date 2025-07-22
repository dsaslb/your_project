"""
다중 인증 시스템 (Multi-Factor Authentication)
TOTP, SMS, 이메일 인증을 지원하는 고급 보안 시스템
"""
import pyotp
import qrcode
import base64
import io
import logging
import hashlib
import secrets
import time
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, Tuple
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import json
import os

logger = logging.getLogger(__name__)

class MultiFactorAuth:
    """다중 인증 시스템 클래스"""
    
    def __init__(self):
        """초기화"""
        self.secret_key = os.getenv('MFA_SECRET_KEY', 'your-secret-key-here')
        self.sms_api_key = os.getenv('SMS_API_KEY', '')
        self.email_smtp_server = os.getenv('EMAIL_SMTP_SERVER', 'smtp.gmail.com')
        self.email_smtp_port = int(os.getenv('EMAIL_SMTP_PORT', '587'))
        self.email_username = os.getenv('EMAIL_USERNAME', '')
        self.email_password = os.getenv('EMAIL_PASSWORD', '')
        
        # 인증 시도 기록
        self.auth_attempts = {}
        self.max_attempts = 5
        self.lockout_duration = 300  # 5분
        
        # 세션 관리
        self.active_sessions = {}
        self.session_timeout = 3600  # 1시간
        
        logger.info("다중 인증 시스템 초기화 완료")
    
    def generate_totp_secret(self, user_id: str) -> str:
        """TOTP 시크릿 키 생성"""
        try:
            # 사용자별 고유 시크릿 생성
            user_secret = f"{self.secret_key}_{user_id}_{int(time.time())}"
            secret = base64.b32encode(hashlib.sha256(user_secret.encode()).digest()).decode()
            return secret
        except Exception as e:
            logger.error(f"TOTP 시크릿 생성 오류: {str(e)}")
            raise
    
    def generate_qr_code(self, user_id: str, email: str, secret: str) -> str:
        """QR 코드 생성 (Google Authenticator용)"""
        try:
            # TOTP URI 생성
            totp_uri = pyotp.totp.TOTP(secret).provisioning_uri(
                name=email,
                issuer_name="Your Program"
            )
            
            # QR 코드 생성
            qr = qrcode.QRCode(version=1, box_size=10, border=5)
            qr.add_data(totp_uri)
            qr.make(fit=True)
            
            # 이미지 생성
            img = qr.make_image(fill_color="black", back_color="white")
            
            # Base64로 인코딩
            buffer = io.BytesIO()
            img.save(buffer, format='PNG')
            img_str = base64.b64encode(buffer.getvalue()).decode()
            
            return f"data:image/png;base64,{img_str}"
        except Exception as e:
            logger.error(f"QR 코드 생성 오류: {str(e)}")
            raise
    
    def verify_totp(self, secret: str, token: str) -> bool:
        """TOTP 토큰 검증"""
        try:
            totp = pyotp.TOTP(secret)
            return totp.verify(token, valid_window=1)  # 30초 윈도우
        except Exception as e:
            logger.error(f"TOTP 검증 오류: {str(e)}")
            return False
    
    def generate_sms_code(self, phone_number: str) -> str:
        """SMS 인증 코드 생성"""
        try:
            # 6자리 숫자 코드 생성
            code = ''.join([str(secrets.randbelow(10)) for _ in range(6)])
            
            # 코드 저장 (실제로는 Redis나 DB에 저장)
            self._store_sms_code(phone_number, code)
            
            # SMS 발송 (실제 구현에서는 SMS API 사용)
            self._send_sms(phone_number, f"인증 코드: {code}")
            
            return code
        except Exception as e:
            logger.error(f"SMS 코드 생성 오류: {str(e)}")
            raise
    
    def verify_sms_code(self, phone_number: str, code: str) -> bool:
        """SMS 인증 코드 검증"""
        try:
            stored_code = self._get_stored_sms_code(phone_number)
            if stored_code and stored_code == code:
                self._clear_sms_code(phone_number)
                return True
            return False
        except Exception as e:
            logger.error(f"SMS 코드 검증 오류: {str(e)}")
            return False
    
    def generate_email_code(self, email: str) -> str:
        """이메일 인증 코드 생성"""
        try:
            # 6자리 숫자 코드 생성
            code = ''.join([str(secrets.randbelow(10)) for _ in range(6)])
            
            # 코드 저장
            self._store_email_code(email, code)
            
            # 이메일 발송
            self._send_email(email, code)
            
            return code
        except Exception as e:
            logger.error(f"이메일 코드 생성 오류: {str(e)}")
            raise
    
    def verify_email_code(self, email: str, code: str) -> bool:
        """이메일 인증 코드 검증"""
        try:
            stored_code = self._get_stored_email_code(email)
            if stored_code and stored_code == code:
                self._clear_email_code(email)
                return True
            return False
        except Exception as e:
            logger.error(f"이메일 코드 검증 오류: {str(e)}")
            return False
    
    def check_auth_attempts(self, user_id: str) -> Dict[str, Any]:
        """인증 시도 확인"""
        if user_id in self.auth_attempts:
            attempts = self.auth_attempts[user_id]
            if attempts['count'] >= self.max_attempts:
                lockout_until = attempts['last_attempt'] + timedelta(seconds=self.lockout_duration)
                if datetime.now() < lockout_until:
                    return {
                        'locked': True,
                        'lockout_until': lockout_until.isoformat(),
                        'remaining_time': (lockout_until - datetime.now()).seconds
                    }
                else:
                    # 잠금 해제
                    del self.auth_attempts[user_id]
        
        return {'locked': False}
    
    def record_auth_attempt(self, user_id: str, success: bool):
        """인증 시도 기록"""
        if user_id not in self.auth_attempts:
            self.auth_attempts[user_id] = {
                'count': 0,
                'last_attempt': datetime.now()
            }
        
        if success:
            # 성공 시 기록 초기화
            del self.auth_attempts[user_id]
        else:
            # 실패 시 카운트 증가
            self.auth_attempts[user_id]['count'] += 1
            self.auth_attempts[user_id]['last_attempt'] = datetime.now()
    
    def create_session(self, user_id: str, auth_methods: list) -> str:
        """보안 세션 생성"""
        try:
            session_id = secrets.token_urlsafe(32)
            session_data = {
                'user_id': user_id,
                'auth_methods': auth_methods,
                'created_at': datetime.now(),
                'expires_at': datetime.now() + timedelta(seconds=self.session_timeout),
                'last_activity': datetime.now()
            }
            
            self.active_sessions[session_id] = session_data
            return session_id
        except Exception as e:
            logger.error(f"세션 생성 오류: {str(e)}")
            raise
    
    def validate_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """세션 검증"""
        try:
            if session_id not in self.active_sessions:
                return None
            
            session = self.active_sessions[session_id]
            
            # 세션 만료 확인
            if datetime.now() > session['expires_at']:
                del self.active_sessions[session_id]
                return None
            
            # 마지막 활동 시간 업데이트
            session['last_activity'] = datetime.now()
            
            return session
        except Exception as e:
            logger.error(f"세션 검증 오류: {str(e)}")
            return None
    
    def revoke_session(self, session_id: str):
        """세션 취소"""
        try:
            if session_id in self.active_sessions:
                del self.active_sessions[session_id]
        except Exception as e:
            logger.error(f"세션 취소 오류: {str(e)}")
    
    def get_auth_status(self, user_id: str) -> Dict[str, Any]:
        """사용자 인증 상태 조회"""
        try:
            lockout_status = self.check_auth_attempts(user_id)
            
            return {
                'user_id': user_id,
                'locked': lockout_status['locked'],
                'lockout_until': lockout_status.get('lockout_until'),
                'remaining_attempts': self.max_attempts - self.auth_attempts.get(user_id, {}).get('count', 0),
                'active_sessions': len([s for s in self.active_sessions.values() if s['user_id'] == user_id])
            }
        except Exception as e:
            logger.error(f"인증 상태 조회 오류: {str(e)}")
            return {}
    
    def _store_sms_code(self, phone_number: str, code: str):
        """SMS 코드 저장 (임시 구현)"""
        # 실제로는 Redis나 DB에 저장
        if not hasattr(self, '_sms_codes'):
            self._sms_codes = {}
        self._sms_codes[phone_number] = {
            'code': code,
            'expires_at': datetime.now() + timedelta(minutes=5)
        }
    
    def _get_stored_sms_code(self, phone_number: str) -> Optional[str]:
        """저장된 SMS 코드 조회"""
        if hasattr(self, '_sms_codes') and phone_number in self._sms_codes:
            stored = self._sms_codes[phone_number]
            if datetime.now() < stored['expires_at']:
                return stored['code']
            else:
                del self._sms_codes[phone_number]
        return None
    
    def _clear_sms_code(self, phone_number: str):
        """SMS 코드 삭제"""
        if hasattr(self, '_sms_codes') and phone_number in self._sms_codes:
            del self._sms_codes[phone_number]
    
    def _store_email_code(self, email: str, code: str):
        """이메일 코드 저장 (임시 구현)"""
        if not hasattr(self, '_email_codes'):
            self._email_codes = {}
        self._email_codes[email] = {
            'code': code,
            'expires_at': datetime.now() + timedelta(minutes=10)
        }
    
    def _get_stored_email_code(self, email: str) -> Optional[str]:
        """저장된 이메일 코드 조회"""
        if hasattr(self, '_email_codes') and email in self._email_codes:
            stored = self._email_codes[email]
            if datetime.now() < stored['expires_at']:
                return stored['code']
            else:
                del self._email_codes[email]
        return None
    
    def _clear_email_code(self, email: str):
        """이메일 코드 삭제"""
        if hasattr(self, '_email_codes') and email in self._email_codes:
            del self._email_codes[email]
    
    def _send_sms(self, phone_number: str, message: str):
        """SMS 발송 (실제 구현에서는 SMS API 사용)"""
        logger.info(f"SMS 발송: {phone_number} - {message}")
        # 실제 구현에서는 SMS API 호출
        # 예: Twilio, AWS SNS 등
    
    def _send_email(self, email: str, code: str):
        """이메일 발송"""
        try:
            if not self.email_username or not self.email_password:
                logger.warning("이메일 설정이 없어 로그로만 기록합니다")
                logger.info(f"이메일 발송: {email} - 인증 코드: {code}")
                return
            
            msg = MIMEMultipart()
            msg['From'] = self.email_username
            msg['To'] = email
            msg['Subject'] = "보안 인증 코드"
            
            body = f"""
            안녕하세요,
            
            보안 인증을 위한 코드입니다:
            
            {code}
            
            이 코드는 10분 후 만료됩니다.
            
            감사합니다.
            """
            
            msg.attach(MIMEText(body, 'plain'))
            
            server = smtplib.SMTP(self.email_smtp_server, self.email_smtp_port)
            server.starttls()
            server.login(self.email_username, self.email_password)
            server.send_message(msg)
            server.quit()
            
            logger.info(f"이메일 발송 완료: {email}")
        except Exception as e:
            logger.error(f"이메일 발송 오류: {str(e)}")
            # 실패해도 로그로 기록
            logger.info(f"이메일 발송: {email} - 인증 코드: {code}")
    
    def cleanup_expired_sessions(self):
        """만료된 세션 정리"""
        try:
            current_time = datetime.now()
            expired_sessions = [
                session_id for session_id, session in self.active_sessions.items()
                if current_time > session['expires_at']
            ]
            
            for session_id in expired_sessions:
                del self.active_sessions[session_id]
            
            if expired_sessions:
                logger.info(f"만료된 세션 {len(expired_sessions)}개 정리 완료")
        except Exception as e:
            logger.error(f"세션 정리 오류: {str(e)}")

# 전역 인스턴스
mfa_system = MultiFactorAuth()

if __name__ == '__main__':
    # 테스트 코드
    print("다중 인증 시스템 테스트")
    
    # TOTP 테스트
    user_id = "test_user"
    email = "test@example.com"
    secret = mfa_system.generate_totp_secret(user_id)
    qr_code = mfa_system.generate_qr_code(user_id, email, secret)
    
    print(f"TOTP Secret: {secret}")
    print(f"QR Code generated: {len(qr_code)} characters")
    
    # SMS 테스트
    phone = "+82-10-1234-5678"
    sms_code = mfa_system.generate_sms_code(phone)
    print(f"SMS Code: {sms_code}")
    
    # 이메일 테스트
    email_code = mfa_system.generate_email_code(email)
    print(f"Email Code: {email_code}")
    
    # 세션 테스트
    session_id = mfa_system.create_session(user_id, ['totp', 'sms'])
    print(f"Session ID: {session_id}")
    
    # 세션 검증
    session = mfa_system.validate_session(session_id)
    print(f"Session valid: {session is not None}")
    
    print("다중 인증 시스템 테스트 완료") 
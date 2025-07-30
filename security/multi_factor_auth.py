"""
다중 인증 시스템 (MFA)
엔터프라이즈급 보안을 위한 다중 인증 시스템
"""

import pyotp
import qrcode
import base64
import hashlib
import secrets
import time
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import requests

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class MFAMethod:
    """MFA 방법 정보"""
    method_type: str  # totp, email, sms, backup_codes
    enabled: bool
    created_at: datetime
    last_used: Optional[datetime]
    secret: Optional[str] = None
    backup_codes: Optional[List[str]] = None
    phone_number: Optional[str] = None
    email: Optional[str] = None

@dataclass
class MFASession:
    """MFA 세션 정보"""
    session_id: str
    user_id: str
    method_type: str
    created_at: datetime
    expires_at: datetime
    verified: bool
    attempts: int
    max_attempts: int = 3

class MultiFactorAuth:
    """다중 인증 시스템"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.sessions: Dict[str, MFASession] = {}
        self.user_methods: Dict[str, List[MFAMethod]] = {}
        
        # TOTP 설정
        self.totp_issuer = config.get('totp_issuer', 'Your Program')
        self.totp_digits = config.get('totp_digits', 6)
        self.totp_interval = config.get('totp_interval', 30)
        
        # 이메일 설정
        self.smtp_config = config.get('smtp', {})
        
        # SMS 설정
        self.sms_config = config.get('sms', {})
        
        # 보안 설정
        self.max_attempts = config.get('max_attempts', 3)
        self.session_timeout = config.get('session_timeout', 300)  # 5분
        self.backup_codes_count = config.get('backup_codes_count', 10)
    
    def generate_totp_secret(self, user_id: str) -> str:
        """TOTP 시크릿 키 생성"""
        # 사용자별 고유 시크릿 생성
        secret = pyotp.random_base32()
        return secret
    
    def generate_totp_qr_code(self, user_id: str, email: str, secret: str) -> str:
        """TOTP QR 코드 생성"""
        # TOTP URI 생성
        totp_uri = pyotp.totp.TOTP(secret).provisioning_uri(
            name=email,
            issuer_name=self.totp_issuer
        )
        
        # QR 코드 생성
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(totp_uri)
        qr.make(fit=True)
        
        # QR 코드를 base64로 인코딩
        img = qr.make_image(fill_color="black", back_color="white")
        import io
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        qr_base64 = base64.b64encode(buffer.getvalue()).decode()
        
        return f"data:image/png;base64,{qr_base64}"
    
    def verify_totp(self, secret: str, token: str) -> bool:
        """TOTP 토큰 검증"""
        try:
            totp = pyotp.TOTP(secret, digits=self.totp_digits, interval=self.totp_interval)
            return totp.verify(token)
        except Exception as e:
            logger.error(f"TOTP 검증 오류: {e}")
            return False
    
    def generate_backup_codes(self, count: int = None) -> List[str]:
        """백업 코드 생성"""
        if count is None:
            count = self.backup_codes_count
        
        codes = []
        for _ in range(count):
            # 8자리 숫자 코드 생성
            code = ''.join(secrets.choice('0123456789') for _ in range(8))
            codes.append(code)
        
        return codes
    
    def verify_backup_code(self, user_id: str, code: str) -> bool:
        """백업 코드 검증"""
        if user_id not in self.user_methods:
            return False
        
        for method in self.user_methods[user_id]:
            if method.method_type == 'backup_codes' and method.backup_codes:
                if code in method.backup_codes:
                    # 사용된 코드 제거
                    method.backup_codes.remove(code)
                    method.last_used = datetime.now()
                    return True
        
        return False
    
    def send_email_code(self, email: str, code: str) -> bool:
        """이메일 인증 코드 전송"""
        try:
            if not self.smtp_config:
                logger.error("SMTP 설정이 없습니다")
                return False
            
            msg = MIMEMultipart()
            msg['From'] = self.smtp_config['from_email']
            msg['To'] = email
            msg['Subject'] = f"{self.totp_issuer} 인증 코드"
            
            body = f"""
            안녕하세요,
            
            {self.totp_issuer} 인증 코드입니다.
            
            인증 코드: {code}
            
            이 코드는 10분간 유효합니다.
            타인에게 공유하지 마세요.
            
            감사합니다.
            {self.totp_issuer} 팀
            """
            
            msg.attach(MIMEText(body, 'plain'))
            
            server = smtplib.SMTP(self.smtp_config['host'], self.smtp_config['port'])
            server.starttls()
            server.login(self.smtp_config['username'], self.smtp_config['password'])
            server.send_message(msg)
            server.quit()
            
            logger.info(f"이메일 인증 코드 전송 완료: {email}")
            return True
            
        except Exception as e:
            logger.error(f"이메일 인증 코드 전송 오류: {e}")
            return False
    
    def send_sms_code(self, phone_number: str, code: str) -> bool:
        """SMS 인증 코드 전송"""
        try:
            if not self.sms_config:
                logger.error("SMS 설정이 없습니다")
                return False
            
            # SMS API 호출 (예: Twilio, AWS SNS 등)
            # 실제 구현에서는 SMS 서비스 API 사용
            logger.info(f"SMS 인증 코드 전송: {phone_number} - {code}")
            return True
            
        except Exception as e:
            logger.error(f"SMS 인증 코드 전송 오류: {e}")
            return False
    
    def generate_email_code(self) -> str:
        """이메일 인증 코드 생성"""
        return ''.join(secrets.choice('0123456789') for _ in range(6))
    
    def generate_sms_code(self) -> str:
        """SMS 인증 코드 생성"""
        return ''.join(secrets.choice('0123456789') for _ in range(6))
    
    def create_mfa_session(self, user_id: str, method_type: str) -> str:
        """MFA 세션 생성"""
        session_id = secrets.token_urlsafe(32)
        expires_at = datetime.now() + timedelta(seconds=self.session_timeout)
        
        session = MFASession(
            session_id=session_id,
            user_id=user_id,
            method_type=method_type,
            created_at=datetime.now(),
            expires_at=expires_at,
            verified=False,
            attempts=0,
            max_attempts=self.max_attempts
        )
        
        self.sessions[session_id] = session
        return session_id
    
    def verify_mfa_session(self, session_id: str, token: str) -> bool:
        """MFA 세션 검증"""
        if session_id not in self.sessions:
            return False
        
        session = self.sessions[session_id]
        
        # 세션 만료 확인
        if datetime.now() > session.expires_at:
            del self.sessions[session_id]
            return False
        
        # 시도 횟수 확인
        if session.attempts >= session.max_attempts:
            del self.sessions[session_id]
            return False
        
        session.attempts += 1
        
        # 토큰 검증
        user_id = session.user_id
        method_type = session.method_type
        
        if user_id not in self.user_methods:
            return False
        
        for method in self.user_methods[user_id]:
            if method.method_type == method_type and method.enabled:
                if method_type == 'totp':
                    verified = self.verify_totp(method.secret, token)
                elif method_type == 'backup_codes':
                    verified = self.verify_backup_code(user_id, token)
                elif method_type in ['email', 'sms']:
                    # 이메일/SMS 코드 검증 (실제로는 저장된 코드와 비교)
                    verified = True  # 임시 구현
                else:
                    verified = False
                
                if verified:
                    session.verified = True
                    method.last_used = datetime.now()
                    return True
        
        return False
    
    def setup_totp(self, user_id: str, email: str) -> Dict[str, str]:
        """TOTP 설정"""
        secret = self.generate_totp_secret(user_id)
        qr_code = self.generate_totp_qr_code(user_id, email, secret)
        
        # MFA 방법 저장
        method = MFAMethod(
            method_type='totp',
            enabled=True,
            created_at=datetime.now(),
            last_used=None,
            secret=secret
        )
        
        if user_id not in self.user_methods:
            self.user_methods[user_id] = []
        
        self.user_methods[user_id].append(method)
        
        return {
            'secret': secret,
            'qr_code': qr_code,
            'backup_codes': self.generate_backup_codes()
        }
    
    def setup_email_mfa(self, user_id: str, email: str) -> bool:
        """이메일 MFA 설정"""
        method = MFAMethod(
            method_type='email',
            enabled=True,
            created_at=datetime.now(),
            last_used=None,
            email=email
        )
        
        if user_id not in self.user_methods:
            self.user_methods[user_id] = []
        
        self.user_methods[user_id].append(method)
        return True
    
    def setup_sms_mfa(self, user_id: str, phone_number: str) -> bool:
        """SMS MFA 설정"""
        method = MFAMethod(
            method_type='sms',
            enabled=True,
            created_at=datetime.now(),
            last_used=None,
            phone_number=phone_number
        )
        
        if user_id not in self.user_methods:
            self.user_methods[user_id] = []
        
        self.user_methods[user_id].append(method)
        return True
    
    def initiate_mfa(self, user_id: str, method_type: str) -> Tuple[str, str]:
        """MFA 시작"""
        if user_id not in self.user_methods:
            raise ValueError("MFA가 설정되지 않았습니다")
        
        # 활성화된 방법 확인
        active_methods = [m for m in self.user_methods[user_id] if m.enabled]
        if not active_methods:
            raise ValueError("활성화된 MFA 방법이 없습니다")
        
        # 세션 생성
        session_id = self.create_mfa_session(user_id, method_type)
        
        # 인증 코드 생성 및 전송
        if method_type == 'email':
            code = self.generate_email_code()
            for method in active_methods:
                if method.method_type == 'email' and method.email:
                    self.send_email_code(method.email, code)
                    break
        elif method_type == 'sms':
            code = self.generate_sms_code()
            for method in active_methods:
                if method.method_type == 'sms' and method.phone_number:
                    self.send_sms_code(method.phone_number, code)
                    break
        else:
            code = ""  # TOTP는 클라이언트에서 생성
        
        return session_id, code
    
    def get_user_mfa_methods(self, user_id: str) -> List[MFAMethod]:
        """사용자 MFA 방법 조회"""
        return self.user_methods.get(user_id, [])
    
    def disable_mfa_method(self, user_id: str, method_type: str) -> bool:
        """MFA 방법 비활성화"""
        if user_id not in self.user_methods:
            return False
        
        for method in self.user_methods[user_id]:
            if method.method_type == method_type:
                method.enabled = False
                return True
        
        return False
    
    def enable_mfa_method(self, user_id: str, method_type: str) -> bool:
        """MFA 방법 활성화"""
        if user_id not in self.user_methods:
            return False
        
        for method in self.user_methods[user_id]:
            if method.method_type == method_type:
                method.enabled = True
                return True
        
        return False
    
    def cleanup_expired_sessions(self):
        """만료된 세션 정리"""
        current_time = datetime.now()
        expired_sessions = [
            session_id for session_id, session in self.sessions.items()
            if current_time > session.expires_at
        ]
        
        for session_id in expired_sessions:
            del self.sessions[session_id]
        
        if expired_sessions:
            logger.info(f"만료된 세션 {len(expired_sessions)}개 정리 완료")

class BiometricAuth:
    """생체 인증 시스템"""
    
    def __init__(self):
        self.supported_methods = ['fingerprint', 'face', 'voice']
    
    def is_biometric_available(self, method: str) -> bool:
        """생체 인증 사용 가능 여부 확인"""
        # 실제 구현에서는 디바이스 하드웨어 확인
        return method in self.supported_methods
    
    def enroll_biometric(self, user_id: str, method: str, biometric_data: str) -> bool:
        """생체 인증 등록"""
        try:
            # 생체 데이터 암호화 및 저장
            # 실제 구현에서는 안전한 저장소 사용
            logger.info(f"생체 인증 등록: {user_id} - {method}")
            return True
        except Exception as e:
            logger.error(f"생체 인증 등록 오류: {e}")
            return False
    
    def verify_biometric(self, user_id: str, method: str, biometric_data: str) -> bool:
        """생체 인증 검증"""
        try:
            # 저장된 생체 데이터와 비교
            # 실제 구현에서는 안전한 검증 로직 사용
            logger.info(f"생체 인증 검증: {user_id} - {method}")
            return True
        except Exception as e:
            logger.error(f"생체 인증 검증 오류: {e}")
            return False

# 사용 예시
if __name__ == "__main__":
    # MFA 설정
    config = {
        'totp_issuer': 'Your Program',
        'totp_digits': 6,
        'totp_interval': 30,
        'max_attempts': 3,
        'session_timeout': 300,
        'backup_codes_count': 10,
        'smtp': {
            'host': 'smtp.gmail.com',
            'port': 587,
            'username': 'your-email@gmail.com',
            'password': 'your-password',
            'from_email': 'noreply@yourprogram.com'
        },
        'sms': {
            'provider': 'twilio',
            'account_sid': 'your-account-sid',
            'auth_token': 'your-auth-token',
            'from_number': '+1234567890'
        }
    }
    
    # MFA 인스턴스 생성
    mfa = MultiFactorAuth(config)
    
    # TOTP 설정
    user_id = "user123"
    email = "user@example.com"
    
    totp_setup = mfa.setup_totp(user_id, email)
    print(f"TOTP 시크릿: {totp_setup['secret']}")
    print(f"백업 코드: {totp_setup['backup_codes']}")
    
    # 이메일 MFA 설정
    mfa.setup_email_mfa(user_id, email)
    
    # MFA 시작
    session_id, code = mfa.initiate_mfa(user_id, 'email')
    print(f"세션 ID: {session_id}")
    print(f"인증 코드: {code}")
    
    # TOTP 검증
    totp = pyotp.TOTP(totp_setup['secret'])
    current_token = totp.now()
    print(f"현재 TOTP 토큰: {current_token}")
    
    # 세션 검증
    verified = mfa.verify_mfa_session(session_id, current_token)
    print(f"검증 결과: {verified}")
    
    # 만료된 세션 정리
    mfa.cleanup_expired_sessions() 
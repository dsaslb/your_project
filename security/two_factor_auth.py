"""
2단계 인증(2FA) 시스템
TOTP, SMS, 이메일 인증 기능 제공
"""

import pyotp
import qrcode
import base64
import io
import logging
import random
import string
from typing import Dict, Optional, Tuple
from datetime import datetime, timedelta
from flask import current_app, request, jsonify
from models_main import User, db
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

logger = logging.getLogger(__name__)

class TwoFactorAuth:
    """2단계 인증 관리자"""
    
    def __init__(self, app=None):
        self.app = app
        self.totp_issuer = "Your Program"
        self.sms_provider = None
        self.email_provider = None
        
        if app:
            self.init_app(app)
    
    def init_app(self, app):
        """Flask 앱에 2FA 초기화"""
        self.app = app
        self.totp_issuer = app.config.get('TOTP_ISSUER', 'Your Program')
        
        # SMS 설정
        self.sms_api_key = app.config.get('SMS_API_KEY')
        self.sms_secret_key = app.config.get('SMS_SECRET_KEY')
        self.sms_from_number = app.config.get('SMS_FROM_NUMBER')
        
        # 이메일 설정
        self.email_host = app.config.get('EMAIL_HOST', 'smtp.gmail.com')
        self.email_port = app.config.get('EMAIL_PORT', 587)
        self.email_username = app.config.get('EMAIL_USERNAME')
        self.email_password = app.config.get('EMAIL_PASSWORD')
        
        logger.info("2단계 인증 시스템 초기화 완료")
    
    def generate_totp_secret(self) -> str:
        """TOTP 시크릿 키 생성"""
        return pyotp.random_base32()
    
    def generate_totp_qr_code(self, user: User, secret: str) -> str:
        """TOTP QR 코드 생성"""
        try:
            # TOTP URI 생성
            totp_uri = pyotp.totp.TOTP(secret).provisioning_uri(
                name=user.email,
                issuer_name=self.totp_issuer
            )
            
            # QR 코드 생성
            qr = qrcode.QRCode(version=1, box_size=10, border=5)
            qr.add_data(totp_uri)
            qr.make(fit=True)
            
            # QR 코드 이미지 생성
            img = qr.make_image(fill_color="black", back_color="white")
            
            # Base64로 인코딩
            buffer = io.BytesIO()
            img.save(buffer, format='PNG')
            qr_code_base64 = base64.b64encode(buffer.getvalue()).decode()
            
            return f"data:image/png;base64,{qr_code_base64}"
            
        except Exception as e:
            logger.error(f"TOTP QR 코드 생성 실패: {e}")
            return None
    
    def verify_totp_code(self, secret: str, code: str) -> bool:
        """TOTP 코드 검증"""
        try:
            totp = pyotp.TOTP(secret)
            return totp.verify(code)
        except Exception as e:
            logger.error(f"TOTP 코드 검증 실패: {e}")
            return False
    
    def generate_sms_code(self) -> str:
        """SMS 인증 코드 생성 (6자리 숫자)"""
        return ''.join(random.choices(string.digits, k=6))
    
    def send_sms_code(self, phone_number: str, code: str) -> bool:
        """SMS 인증 코드 전송"""
        try:
            # 실제 SMS 서비스 연동 (예: 네이버 클라우드 플랫폼)
            if not all([self.sms_api_key, self.sms_secret_key, self.sms_from_number]):
                logger.warning("SMS 설정이 완료되지 않았습니다")
                return False
            
            # SMS 전송 로직 (실제 구현에서는 SMS 서비스 API 호출)
            message = f"[{self.totp_issuer}] 인증 코드: {code}"
            
            # 임시로 로그만 출력
            logger.info(f"SMS 전송: {phone_number} -> {code}")
            
            return True
            
        except Exception as e:
            logger.error(f"SMS 전송 실패: {e}")
            return False
    
    def send_email_code(self, email: str, code: str) -> bool:
        """이메일 인증 코드 전송"""
        try:
            if not all([self.email_username, self.email_password]):
                logger.warning("이메일 설정이 완료되지 않았습니다")
                return False
            
            # 이메일 메시지 생성
            msg = MIMEMultipart()
            msg['From'] = self.email_username
            msg['To'] = email
            msg['Subject'] = f"[{self.totp_issuer}] 2단계 인증 코드"
            
            body = f"""
            안녕하세요!
            
            {self.totp_issuer} 2단계 인증 코드입니다.
            
            인증 코드: {code}
            
            이 코드는 5분간 유효합니다.
            본인이 요청하지 않은 경우 무시하세요.
            
            감사합니다.
            """
            
            msg.attach(MIMEText(body, 'plain'))
            
            # 이메일 전송
            server = smtplib.SMTP(self.email_host, self.email_port)
            server.starttls()
            server.login(self.email_username, self.email_password)
            text = msg.as_string()
            server.sendmail(self.email_username, email, text)
            server.quit()
            
            logger.info(f"이메일 전송: {email} -> {code}")
            return True
            
        except Exception as e:
            logger.error(f"이메일 전송 실패: {e}")
            return False
    
    def generate_backup_codes(self, count: int = 10) -> list:
        """백업 코드 생성"""
        codes = []
        for _ in range(count):
            # 8자리 알파벳+숫자 조합
            code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
            codes.append(code)
        return codes
    
    def verify_backup_code(self, user: User, code: str) -> bool:
        """백업 코드 검증"""
        try:
            backup_codes = getattr(user, 'backup_codes', [])
            if not backup_codes:
                return False
            
            # 코드 검증
            if code.upper() in backup_codes:
                # 사용된 백업 코드 제거
                backup_codes.remove(code.upper())
                user.backup_codes = backup_codes
                db.session.commit()
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"백업 코드 검증 실패: {e}")
            return False
    
    def setup_totp(self, user: User) -> Dict[str, str]:
        """TOTP 2FA 설정"""
        try:
            # TOTP 시크릿 생성
            secret = self.generate_totp_secret()
            
            # QR 코드 생성
            qr_code = self.generate_totp_qr_code(user, secret)
            
            # 백업 코드 생성
            backup_codes = self.generate_backup_codes()
            
            return {
                'secret': secret,
                'qr_code': qr_code,
                'backup_codes': backup_codes
            }
            
        except Exception as e:
            logger.error(f"TOTP 설정 실패: {e}")
            return None
    
    def enable_totp(self, user: User, secret: str, backup_codes: list) -> bool:
        """TOTP 2FA 활성화"""
        try:
            user.totp_secret = secret
            user.backup_codes = backup_codes
            user.two_factor_enabled = True
            user.two_factor_method = 'totp'
            db.session.commit()
            
            logger.info(f"TOTP 2FA 활성화: {user.email}")
            return True
            
        except Exception as e:
            logger.error(f"TOTP 활성화 실패: {e}")
            db.session.rollback()
            return False
    
    def disable_2fa(self, user: User) -> bool:
        """2FA 비활성화"""
        try:
            user.totp_secret = None
            user.backup_codes = None
            user.two_factor_enabled = False
            user.two_factor_method = None
            db.session.commit()
            
            logger.info(f"2FA 비활성화: {user.email}")
            return True
            
        except Exception as e:
            logger.error(f"2FA 비활성화 실패: {e}")
            db.session.rollback()
            return False
    
    def verify_2fa(self, user: User, code: str, method: str = None) -> bool:
        """2FA 코드 검증"""
        try:
            if not user.two_factor_enabled:
                return True  # 2FA가 비활성화된 경우 항상 성공
            
            method = method or user.two_factor_method
            
            if method == 'totp':
                return self.verify_totp_code(user.totp_secret, code)
            elif method == 'sms':
                # SMS 코드 검증 (실제로는 세션/캐시에서 확인)
                return self._verify_sms_code(user, code)
            elif method == 'email':
                # 이메일 코드 검증 (실제로는 세션/캐시에서 확인)
                return self._verify_email_code(user, code)
            elif method == 'backup':
                return self.verify_backup_code(user, code)
            else:
                return False
                
        except Exception as e:
            logger.error(f"2FA 검증 실패: {e}")
            return False
    
    def _verify_sms_code(self, user: User, code: str) -> bool:
        """SMS 코드 검증 (임시 구현)"""
        # 실제로는 Redis나 세션에서 저장된 코드와 비교
        # 여기서는 임시로 True 반환
        return True
    
    def _verify_email_code(self, user: User, code: str) -> bool:
        """이메일 코드 검증 (임시 구현)"""
        # 실제로는 Redis나 세션에서 저장된 코드와 비교
        # 여기서는 임시로 True 반환
        return True
    
    def get_2fa_status(self, user: User) -> Dict[str, any]:
        """2FA 상태 조회"""
        return {
            'enabled': user.two_factor_enabled,
            'method': user.two_factor_method,
            'totp_setup': bool(user.totp_secret),
            'backup_codes_count': len(getattr(user, 'backup_codes', []))
        }

# 전역 2FA 관리자 인스턴스
two_factor_auth = TwoFactorAuth() 
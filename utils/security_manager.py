import hashlib
import hmac
import secrets
import time
import jwt
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64
import os

class SecurityManager:
    """고급 보안 관리 시스템"""
    
    def __init__(self, secret_key: Optional[str] = None):
        self.secret_key = secret_key or os.environ.get('JWT_SECRET_KEY') or 'your-secret-key'
        self.encryption_key = self._generate_encryption_key()
        self.fernet = Fernet(self.encryption_key)
        
        # 로깅 설정
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        # 보안 이벤트 로그
        self.security_events = []
        
        # 세션 관리
        self.active_sessions = {}
        self.session_timeout = 3600  # 1시간
        
        # 로그인 시도 제한
        self.login_attempts = {}
        self.max_login_attempts = 5
        self.lockout_duration = 900  # 15분
        
        # API 요청 제한
        self.api_requests = {}
        self.max_api_requests = 100  # 1분당
        self.api_window = 60  # 1분
    
    def _generate_encryption_key(self) -> bytes:
        """암호화 키 생성"""
        salt = b'your_program_security_salt'
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(self.secret_key.encode()))
        return key
    
    def generate_jwt_token(self, user_id: int, role: str, expires_in: int = 3600) -> str:
        """JWT 토큰 생성"""
        try:
            payload = {
                'user_id': user_id,
                'role': role,
                'exp': datetime.utcnow() + timedelta(seconds=expires_in),
                'iat': datetime.utcnow()
            }
            
            token = jwt.encode(payload, self.secret_key, algorithm='HS256')
            return token
        except Exception as e:
            self.logger.error(f"JWT 토큰 생성 실패: {e}")
            raise
    
    def verify_jwt_token(self, token: str) -> Optional[Dict]:
        """JWT 토큰 검증"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=['HS256'])
            
            # 토큰 만료 확인
            if datetime.utcnow().timestamp() > payload['exp']:
                self._log_security_event('token_expired', payload.get('user_id'), 'Token expired')
                return None
            
            # 세션 활동 업데이트
            for session_id, session in self.active_sessions.items():
                if session.get('token') == token:
                    session['last_activity'] = datetime.utcnow()
                    break
            
            self._log_security_event('token_verified', payload.get('user_id'), 'Token verified')
            return payload
            
        except jwt.ExpiredSignatureError:
            self._log_security_event('token_expired', None, 'Token expired')
            return None
        except jwt.InvalidTokenError as e:
            self._log_security_event('token_invalid', None, f'Invalid token: {str(e)}')
            return None
    
    def encrypt_data(self, data: str) -> str:
        """데이터 암호화"""
        try:
            encrypted_data = self.fernet.encrypt(data.encode())
            return base64.urlsafe_b64encode(encrypted_data).decode()
        except Exception as e:
            self.logger.error(f"데이터 암호화 실패: {e}")
            raise
    
    def decrypt_data(self, encrypted_data: str) -> str:
        """데이터 복호화"""
        try:
            decoded_data = base64.urlsafe_b64decode(encrypted_data.encode())
            decrypted_data = self.fernet.decrypt(decoded_data)
            return decrypted_data.decode()
        except Exception as e:
            self.logger.error(f"데이터 복호화 실패: {e}")
            raise
    
    def hash_password(self, password: str, salt: str = None) -> Tuple[str, str]:
        """비밀번호 해싱"""
        if not salt:
            salt = secrets.token_hex(16)
        
        # PBKDF2를 사용한 안전한 해싱
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt.encode(),
            iterations=100000,
        )
        
        hash_value = base64.urlsafe_b64encode(kdf.derive(password.encode())).decode()
        return hash_value, salt
    
    def verify_password(self, password: str, hash_value: str, salt: str) -> bool:
        """비밀번호 검증"""
        try:
            expected_hash, _ = self.hash_password(password, salt)
            return hmac.compare_digest(hash_value, expected_hash)
        except Exception as e:
            self.logger.error(f"비밀번호 검증 실패: {e}")
            return False
    
    def check_login_attempts(self, user_id: int) -> Tuple[bool, int]:
        """로그인 시도 확인"""
        current_time = time.time()
        
        if user_id not in self.login_attempts:
            return True, 0
        
        attempts = self.login_attempts[user_id]
        
        # 잠금 시간 확인
        if attempts.get('locked_until', 0) > current_time:
            remaining_time = int(attempts['locked_until'] - current_time)
            return False, remaining_time
        
        # 잠금 해제
        if attempts.get('locked_until', 0) <= current_time:
            del self.login_attempts[user_id]
            return True, 0
        
        # 시도 횟수 확인
        attempt_count = attempts.get('count', 0)
        if attempt_count >= self.max_login_attempts:
            # 계정 잠금
            self.login_attempts[user_id] = {
                'count': attempt_count,
                'locked_until': current_time + self.lockout_duration
            }
            self._log_security_event('account_locked', user_id, f'Too many login attempts: {attempt_count}')
            return False, self.lockout_duration
        
        return True, 0
    
    def record_login_attempt(self, user_id: int, success: bool):
        """로그인 시도 기록"""
        current_time = time.time()
        
        if user_id not in self.login_attempts:
            self.login_attempts[user_id] = {'count': 0, 'last_attempt': current_time}
        
        if success:
            # 성공 시 카운터 리셋
            del self.login_attempts[user_id]
            self._log_security_event('login_success', user_id, 'Login successful')
        else:
            # 실패 시 카운터 증가
            self.login_attempts[user_id]['count'] += 1
            self.login_attempts[user_id]['last_attempt'] = current_time
            self._log_security_event('login_failed', user_id, f'Failed attempt: {self.login_attempts[user_id]["count"]}')
    
    def check_api_rate_limit(self, user_id: int, endpoint: str) -> bool:
        """API 요청 제한 확인"""
        current_time = time.time()
        key = f"{user_id}:{endpoint}"
        
        if key not in self.api_requests:
            self.api_requests[key] = []
        
        # 오래된 요청 제거
        self.api_requests[key] = [
            req_time for req_time in self.api_requests[key]
            if current_time - req_time < self.api_window
        ]
        
        # 요청 수 확인
        if len(self.api_requests[key]) >= self.max_api_requests:
            self._log_security_event('rate_limit_exceeded', user_id, f'Endpoint: {endpoint}')
            return False
        
        # 새 요청 추가
        self.api_requests[key].append(current_time)
        return True
    
    def generate_secure_token(self, length: int = 32) -> str:
        """보안 토큰 생성"""
        return secrets.token_urlsafe(length)
    
    def validate_input(self, data: str, max_length: int = 1000) -> bool:
        """입력 데이터 검증"""
        if not data or len(data) > max_length:
            return False
        
        # 위험한 문자 패턴 확인
        dangerous_patterns = [
            '<script', 'javascript:', 'onload=', 'onerror=',
            'union select', 'drop table', 'delete from',
            '../', '..\\', 'file://', 'data:'
        ]
        
        data_lower = data.lower()
        for pattern in dangerous_patterns:
            if pattern in data_lower:
                self._log_security_event('suspicious_input', None, f'Pattern detected: {pattern}')
                return False
        
        return True
    
    def sanitize_filename(self, filename: str) -> str:
        """파일명 정리"""
        # 위험한 문자 제거
        dangerous_chars = ['<', '>', ':', '"', '|', '?', '*', '\\', '/']
        for char in dangerous_chars:
            filename = filename.replace(char, '_')
        
        # 경로 조작 방지
        filename = os.path.basename(filename)
        
        return filename
    
    def _log_security_event(self, event_type: str, user_id: Optional[int], details: str):
        """보안 이벤트 로그"""
        event = {
            'timestamp': datetime.utcnow(),
            'event_type': event_type,
            'user_id': user_id,
            'details': details,
            'ip_address': '127.0.0.1'  # 실제로는 request에서 가져와야 함
        }
        
        self.security_events.append(event)
        
        # 로그 파일에 저장
        log_message = f"[{event['timestamp']}] {event_type} - User: {user_id or 'Unknown'} - {details}"
        self.logger.info(log_message)
        
        # 로그 크기 제한 (최근 1000개만 유지)
        if len(self.security_events) > 1000:
            self.security_events = self.security_events[-1000:]
    
    def get_security_events(self, limit: int = 100) -> List[Dict]:
        """보안 이벤트 조회"""
        return self.security_events[-limit:]
    
    def cleanup_expired_sessions(self):
        """만료된 세션 정리"""
        current_time = datetime.utcnow()
        expired_sessions = []
        
        for session_id, session in self.active_sessions.items():
            if (current_time - session['last_activity']).total_seconds() > self.session_timeout:
                expired_sessions.append(session_id)
        
        for session_id in expired_sessions:
            del self.active_sessions[session_id]
            self._log_security_event('session_expired', None, f'Session: {session_id}')
    
    def get_security_status(self) -> Dict:
        """보안 상태 정보"""
        self.cleanup_expired_sessions()
        
        return {
            'active_sessions': len(self.active_sessions),
            'locked_accounts': len([acc for acc in self.login_attempts.values() 
                                  if acc.get('locked_until', 0) > time.time()]),
            'recent_security_events': len(self.security_events),
            'api_rate_limits': len(self.api_requests)
        }

# 전역 보안 매니저 인스턴스
security_manager = SecurityManager() 

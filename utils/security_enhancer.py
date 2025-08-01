import hashlib
import secrets
import string
import re
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import jwt
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64
import os

class SecurityEnhancer:
    def __init__(self, secret_key: str = None):
        self.logger = logging.getLogger(__name__)
        self.secret_key = secret_key or os.getenv('SECRET_KEY', 'default-secret-key')
        self.encryption_key = self._generate_encryption_key()
        self.cipher_suite = Fernet(self.encryption_key)
        self.security_events = []
        
    def _generate_encryption_key(self) -> bytes:
        """암호화 키 생성"""
        salt = os.urandom(16)
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(self.secret_key.encode()))
        return key
    
    def generate_secure_password(self, length: int = 16) -> str:
        """보안 강화된 비밀번호 생성"""
        if length < 8:
            length = 8
            
        # 문자 세트 정의
        lowercase = string.ascii_lowercase
        uppercase = string.ascii_uppercase
        digits = string.digits
        symbols = "!@#$%^&*()_+-=[]{}|;:,.<>?"
        
        # 각 카테고리에서 최소 1개씩 포함
        password = [
            secrets.choice(lowercase),
            secrets.choice(uppercase),
            secrets.choice(digits),
            secrets.choice(symbols)
        ]
        
        # 나머지 길이만큼 랜덤 선택
        all_chars = lowercase + uppercase + digits + symbols
        password.extend(secrets.choice(all_chars) for _ in range(length - 4))
        
        # 순서 섞기
        password_list = list(password)
        secrets.SystemRandom().shuffle(password_list)
        
        return ''.join(password_list)
    
    def validate_password_strength(self, password: str) -> Dict[str, Any]:
        """비밀번호 강도 검증"""
        score = 0
        feedback = []
        
        # 길이 검사
        if len(password) >= 8:
            score += 1
        else:
            feedback.append("비밀번호는 최소 8자 이상이어야 합니다.")
        
        if len(password) >= 12:
            score += 1
        else:
            feedback.append("12자 이상 권장")
        
        # 문자 종류 검사
        if re.search(r'[a-z]', password):
            score += 1
        else:
            feedback.append("소문자 포함 필요")
            
        if re.search(r'[A-Z]', password):
            score += 1
        else:
            feedback.append("대문자 포함 필요")
            
        if re.search(r'\d', password):
            score += 1
        else:
            feedback.append("숫자 포함 필요")
            
        if re.search(r'[!@#$%^&*()_+\-=\[\]{}|;:,.<>?]', password):
            score += 1
        else:
            feedback.append("특수문자 포함 필요")
        
        # 연속된 문자 검사
        if re.search(r'(.)\1{2,}', password):
            score -= 1
            feedback.append("연속된 동일 문자 사용 금지")
        
        # 일반적인 패턴 검사
        common_patterns = ['123', 'abc', 'qwe', 'password', 'admin']
        for pattern in common_patterns:
            if pattern.lower() in password.lower():
                score -= 2
                feedback.append(f"일반적인 패턴 '{pattern}' 사용 금지")
                break
        
        # 강도 레벨 결정
        if score >= 5:
            strength = "매우 강함"
        elif score >= 4:
            strength = "강함"
        elif score >= 3:
            strength = "보통"
        elif score >= 2:
            strength = "약함"
        else:
            strength = "매우 약함"
        
        return {
            'score': score,
            'strength': strength,
            'feedback': feedback,
            'is_secure': score >= 4
        }
    
    def encrypt_sensitive_data(self, data: str) -> str:
        """민감한 데이터 암호화"""
        try:
            encrypted_data = self.cipher_suite.encrypt(data.encode())
            return base64.urlsafe_b64encode(encrypted_data).decode()
        except Exception as e:
            self.logger.error(f"데이터 암호화 중 오류: {e}")
            raise
    
    def decrypt_sensitive_data(self, encrypted_data: str) -> str:
        """암호화된 데이터 복호화"""
        try:
            decoded_data = base64.urlsafe_b64decode(encrypted_data.encode())
            decrypted_data = self.cipher_suite.decrypt(decoded_data)
            return decrypted_data.decode()
        except Exception as e:
            self.logger.error(f"데이터 복호화 중 오류: {e}")
            raise
    
    def generate_secure_token(self, payload: Dict[str, Any], expires_in: int = 3600) -> str:
        """보안 강화된 JWT 토큰 생성"""
        try:
            # 토큰에 추가 보안 정보 포함
            enhanced_payload = {
                **payload,
                'iat': datetime.utcnow(),
                'exp': datetime.utcnow() + timedelta(seconds=expires_in),
                'jti': secrets.token_urlsafe(32),  # 고유 토큰 ID
                'iss': 'secure-system',  # 발급자
                'aud': 'api-users'  # 대상
            }
            
            token = jwt.encode(enhanced_payload, self.secret_key, algorithm='HS256')
            return token
            
        except Exception as e:
            self.logger.error(f"토큰 생성 중 오류: {e}")
            raise
    
    def verify_secure_token(self, token: str) -> Dict[str, Any]:
        """보안 토큰 검증"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=['HS256'])
            
            # 토큰 사용 여부 확인 (블랙리스트 체크 등)
            if self._is_token_blacklisted(payload.get('jti')):
                raise jwt.InvalidTokenError("토큰이 무효화되었습니다.")
            
            return payload
            
        except jwt.ExpiredSignatureError:
            raise jwt.ExpiredSignatureError("토큰이 만료되었습니다.")
        except jwt.InvalidTokenError as e:
            self.logger.warning(f"잘못된 토큰 시도: {e}")
            raise
        except Exception as e:
            self.logger.error(f"토큰 검증 중 오류: {e}")
            raise
    
    def _is_token_blacklisted(self, jti: str) -> bool:
        """토큰 블랙리스트 확인 (실제로는 DB에서 확인)"""
        # 실제 구현에서는 데이터베이스에서 확인
        return False
    
    def log_security_event(self, event_type: str, details: Dict[str, Any], user_id: str = None):
        """보안 이벤트 로깅"""
        event = {
            'timestamp': datetime.now().isoformat(),
            'event_type': event_type,
            'details': details,
            'user_id': user_id,
            'ip_address': self._get_client_ip(),
            'user_agent': self._get_user_agent()
        }
        
        self.security_events.append(event)
        self.logger.info(f"보안 이벤트: {event_type} - {details}")
        
        # 중요 이벤트는 별도 처리
        if event_type in ['failed_login', 'suspicious_activity', 'unauthorized_access']:
            self._handle_critical_security_event(event)
    
    def _get_client_ip(self) -> str:
        """클라이언트 IP 주소 가져오기 (Flask 컨텍스트 필요)"""
        try:
            from flask import request
            return request.remote_addr
        except:
            return "unknown"
    
    def _get_user_agent(self) -> str:
        """사용자 에이전트 가져오기 (Flask 컨텍스트 필요)"""
        try:
            from flask import request
            return request.headers.get('User-Agent', 'unknown')
        except:
            return "unknown"
    
    def _handle_critical_security_event(self, event: Dict[str, Any]):
        """중요 보안 이벤트 처리"""
        # 실제 구현에서는 알림 발송, 계정 잠금 등
        self.logger.warning(f"중요 보안 이벤트 발생: {event}")
    
    def detect_suspicious_activity(self, user_id: str, action: str, context: Dict[str, Any]) -> bool:
        """의심스러운 활동 탐지"""
        # 사용자별 활동 패턴 분석
        recent_events = [e for e in self.security_events 
                        if e.get('user_id') == user_id 
                        and datetime.fromisoformat(e['timestamp']) > datetime.now() - timedelta(hours=1)]
        
        # 빈도 기반 탐지
        if len(recent_events) > 100:  # 1시간 내 100회 이상 활동
            self.log_security_event('suspicious_activity', {
                'reason': 'high_frequency_activity',
                'count': len(recent_events),
                'action': action
            }, user_id)
            return True
        
        # 패턴 기반 탐지
        failed_logins = [e for e in recent_events if e.get('event_type') == 'failed_login']
        if len(failed_logins) > 5:  # 1시간 내 5회 이상 로그인 실패
            self.log_security_event('suspicious_activity', {
                'reason': 'multiple_failed_logins',
                'count': len(failed_logins),
                'action': action
            }, user_id)
            return True
        
        return False
    
    def generate_security_report(self) -> Dict[str, Any]:
        """보안 리포트 생성"""
        try:
            # 최근 24시간 이벤트 분석
            recent_events = [e for e in self.security_events 
                           if datetime.fromisoformat(e['timestamp']) > datetime.now() - timedelta(days=1)]
            
            # 이벤트 타입별 통계
            event_counts = {}
            for event in recent_events:
                event_type = event.get('event_type', 'unknown')
                event_counts[event_type] = event_counts.get(event_type, 0) + 1
            
            # 의심스러운 활동 분석
            suspicious_events = [e for e in recent_events if e.get('event_type') == 'suspicious_activity']
            
            # 보안 점수 계산
            security_score = 100
            if len(suspicious_events) > 0:
                security_score -= len(suspicious_events) * 10
            if event_counts.get('failed_login', 0) > 10:
                security_score -= 20
            if event_counts.get('unauthorized_access', 0) > 0:
                security_score -= 30
            
            security_score = max(0, security_score)
            
            return {
                'security_score': security_score,
                'total_events_24h': len(recent_events),
                'event_breakdown': event_counts,
                'suspicious_activities': len(suspicious_events),
                'recent_suspicious_events': suspicious_events[-5:],  # 최근 5개
                'recommendations': self._generate_security_recommendations(event_counts, suspicious_events),
                'report_generated_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"보안 리포트 생성 중 오류: {e}")
            return {'error': str(e)}
    
    def _generate_security_recommendations(self, event_counts: Dict, suspicious_events: List) -> List[str]:
        """보안 권장사항 생성"""
        recommendations = []
        
        if event_counts.get('failed_login', 0) > 10:
            recommendations.append("로그인 실패 횟수가 많습니다. 계정 잠금 정책 강화 고려")
        
        if len(suspicious_events) > 0:
            recommendations.append("의심스러운 활동이 감지되었습니다. 추가 모니터링 필요")
        
        if event_counts.get('unauthorized_access', 0) > 0:
            recommendations.append("무단 접근 시도가 있었습니다. 접근 제어 정책 검토 필요")
        
        if not recommendations:
            recommendations.append("현재 보안 상태가 양호합니다. 정기적인 모니터링 유지")
        
        return recommendations
    
    def sanitize_input(self, input_data: str) -> str:
        """사용자 입력 데이터 정제"""
        # XSS 방지
        sanitized = input_data.replace('<', '&lt;').replace('>', '&gt;')
        sanitized = sanitized.replace('"', '&quot;').replace("'", '&#x27;')
        
        # SQL 인젝션 방지 (기본적인 패턴)
        sql_patterns = ['SELECT', 'INSERT', 'UPDATE', 'DELETE', 'DROP', 'CREATE', 'ALTER']
        for pattern in sql_patterns:
            sanitized = sanitized.replace(pattern, f'[BLOCKED_{pattern}]')
        
        return sanitized
    
    def validate_file_upload(self, filename: str, file_size: int, allowed_extensions: List[str] = None) -> Dict[str, Any]:
        """파일 업로드 보안 검증"""
        if allowed_extensions is None:
            allowed_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.pdf', '.doc', '.docx']
        
        result = {
            'is_valid': True,
            'errors': []
        }
        
        # 파일 확장자 검사
        file_ext = os.path.splitext(filename)[1].lower()
        if file_ext not in allowed_extensions:
            result['is_valid'] = False
            result['errors'].append(f"허용되지 않는 파일 형식: {file_ext}")
        
        # 파일 크기 검사 (10MB 제한)
        max_size = 10 * 1024 * 1024  # 10MB
        if file_size > max_size:
            result['is_valid'] = False
            result['errors'].append(f"파일 크기가 너무 큽니다: {file_size} bytes")
        
        # 파일명 보안 검사
        if '..' in filename or '/' in filename or '\\' in filename:
            result['is_valid'] = False
            result['errors'].append("잘못된 파일명입니다")
        
        return result

# 전역 보안 강화기 인스턴스
security_enhancer = SecurityEnhancer() 
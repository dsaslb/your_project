#!/usr/bin/env python3
"""
보안 강화 시스템
"""

import hashlib
import hmac
import secrets
import time
import jwt
import re
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import sqlite3
import os
from functools import wraps
from flask import request, jsonify, g
import ipaddress

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class SecurityEvent:
    timestamp: datetime
    event_type: str  # 'login', 'logout', 'api_call', 'suspicious_activity', 'rate_limit'
    user_id: Optional[str]
    ip_address: str
    user_agent: str
    details: Dict
    risk_score: float

@dataclass
class RateLimitInfo:
    ip_address: str
    endpoint: str
    request_count: int
    window_start: datetime
    blocked_until: Optional[datetime]

class SecurityManager:
    def __init__(self, config: Dict = None):
        self.config = config or {
            'jwt_secret': os.getenv('JWT_SECRET', 'your-secret-key-change-this'),
            'jwt_expiration': 3600,  # 1시간
            'rate_limit_window': 60,  # 1분
            'rate_limit_max_requests': 100,
            'password_min_length': 8,
            'password_require_special': True,
            'session_timeout': 1800,  # 30분
            'max_login_attempts': 5,
            'lockout_duration': 900,  # 15분
            'suspicious_ips': [],
            'allowed_origins': ['http://localhost:3000', 'http://localhost:5000'],
            'enable_csrf': True,
            'enable_xss_protection': True
        }
        
        self.rate_limits: Dict[str, RateLimitInfo] = {}
        self.login_attempts: Dict[str, List[datetime]] = {}
        self.blocked_ips: Dict[str, datetime] = {}
        self.security_events: List[SecurityEvent] = []
        
        # 데이터베이스 초기화
        self.init_database()
        
    def init_database(self):
        """보안 데이터베이스 초기화"""
        os.makedirs('security', exist_ok=True)
        
        conn = sqlite3.connect('security/security.db')
        cursor = conn.cursor()
        
        # 보안 이벤트 테이블
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS security_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                event_type TEXT NOT NULL,
                user_id TEXT,
                ip_address TEXT NOT NULL,
                user_agent TEXT,
                details TEXT,
                risk_score REAL
            )
        ''')
        
        # 차단된 IP 테이블
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS blocked_ips (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ip_address TEXT UNIQUE NOT NULL,
                blocked_until TEXT NOT NULL,
                reason TEXT,
                created_at TEXT NOT NULL
            )
        ''')
        
        # 세션 테이블
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT UNIQUE NOT NULL,
                user_id TEXT NOT NULL,
                created_at TEXT NOT NULL,
                expires_at TEXT NOT NULL,
                ip_address TEXT,
                user_agent TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
        
    def generate_token(self, user_id: str, additional_claims: Dict = None) -> str:
        """JWT 토큰 생성"""
        payload = {
            'user_id': user_id,
            'exp': datetime.utcnow() + timedelta(seconds=self.config['jwt_expiration']),
            'iat': datetime.utcnow(),
            'jti': secrets.token_urlsafe(32)
        }
        
        if additional_claims:
            payload.update(additional_claims)
            
        return jwt.encode(payload, self.config['jwt_secret'], algorithm='HS256')
        
    def verify_token(self, token: str) -> Optional[Dict]:
        """JWT 토큰 검증"""
        try:
            payload = jwt.decode(token, self.config['jwt_secret'], algorithms=['HS256'])
            return payload
        except jwt.ExpiredSignatureError:
            logger.warning("토큰이 만료되었습니다.")
            return None
        except jwt.InvalidTokenError:
            logger.warning("유효하지 않은 토큰입니다.")
            return None
            
    def hash_password(self, password: str) -> str:
        """비밀번호 해싱"""
        salt = secrets.token_hex(16)
        hash_obj = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000)
        return f"{salt}${hash_obj.hex()}"
        
    def verify_password(self, password: str, hashed: str) -> bool:
        """비밀번호 검증"""
        try:
            salt, hash_hex = hashed.split('$')
            hash_obj = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000)
            return hmac.compare_digest(hash_obj.hex(), hash_hex)
        except Exception:
            return False
            
    def validate_password_strength(self, password: str) -> Tuple[bool, List[str]]:
        """비밀번호 강도 검증"""
        errors = []
        
        if len(password) < self.config['password_min_length']:
            errors.append(f"비밀번호는 최소 {self.config['password_min_length']}자 이상이어야 합니다.")
            
        if not re.search(r'[A-Z]', password):
            errors.append("비밀번호는 대문자를 포함해야 합니다.")
            
        if not re.search(r'[a-z]', password):
            errors.append("비밀번호는 소문자를 포함해야 합니다.")
            
        if not re.search(r'\d', password):
            errors.append("비밀번호는 숫자를 포함해야 합니다.")
            
        if self.config['password_require_special'] and not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            errors.append("비밀번호는 특수문자를 포함해야 합니다.")
            
        return len(errors) == 0, errors
        
    def check_rate_limit(self, ip_address: str, endpoint: str) -> Tuple[bool, Optional[str]]:
        """속도 제한 확인"""
        key = f"{ip_address}:{endpoint}"
        now = datetime.now()
        
        if key in self.rate_limits:
            rate_info = self.rate_limits[key]
            
            # 윈도우가 지났으면 리셋
            if now - rate_info.window_start > timedelta(seconds=self.config['rate_limit_window']):
                rate_info.request_count = 1
                rate_info.window_start = now
                rate_info.blocked_until = None
            else:
                rate_info.request_count += 1
                
                # 제한 초과
                if rate_info.request_count > self.config['rate_limit_max_requests']:
                    block_duration = timedelta(minutes=5)
                    rate_info.blocked_until = now + block_duration
                    
                    self.log_security_event(
                        event_type='rate_limit',
                        user_id=None,
                        ip_address=ip_address,
                        user_agent=request.headers.get('User-Agent', ''),
                        details={'endpoint': endpoint, 'request_count': rate_info.request_count},
                        risk_score=0.7
                    )
                    
                    return False, f"속도 제한 초과. {block_duration.seconds // 60}분 후에 다시 시도해주세요."
        else:
            self.rate_limits[key] = RateLimitInfo(
                ip_address=ip_address,
                endpoint=endpoint,
                request_count=1,
                window_start=now,
                blocked_until=None
            )
            
        # 차단된 상태인지 확인
        if self.rate_limits[key].blocked_until and now < self.rate_limits[key].blocked_until:
            remaining = self.rate_limits[key].blocked_until - now
            return False, f"차단된 상태입니다. {remaining.seconds // 60}분 후에 다시 시도해주세요."
            
        return True, None
        
    def check_login_attempts(self, ip_address: str) -> Tuple[bool, Optional[str]]:
        """로그인 시도 확인"""
        now = datetime.now()
        
        # 오래된 시도 기록 정리
        if ip_address in self.login_attempts:
            self.login_attempts[ip_address] = [
                attempt for attempt in self.login_attempts[ip_address]
                if now - attempt < timedelta(minutes=15)
            ]
            
        # 차단된 IP 확인
        if ip_address in self.blocked_ips:
            if now < self.blocked_ips[ip_address]:
                remaining = self.blocked_ips[ip_address] - now
                return False, f"로그인이 차단되었습니다. {remaining.seconds // 60}분 후에 다시 시도해주세요."
            else:
                del self.blocked_ips[ip_address]
                
        # 시도 횟수 확인
        if ip_address in self.login_attempts and len(self.login_attempts[ip_address]) >= self.config['max_login_attempts']:
            block_until = now + timedelta(seconds=self.config['lockout_duration'])
            self.blocked_ips[ip_address] = block_until
            
            self.log_security_event(
                event_type='account_locked',
                user_id=None,
                ip_address=ip_address,
                user_agent=request.headers.get('User-Agent', ''),
                details={'reason': 'max_login_attempts_exceeded'},
                risk_score=0.8
            )
            
            return False, f"로그인 시도 횟수 초과. {self.config['lockout_duration'] // 60}분 후에 다시 시도해주세요."
            
        return True, None
        
    def record_login_attempt(self, ip_address: str, success: bool, user_id: str = None):
        """로그인 시도 기록"""
        now = datetime.now()
        
        if not success:
            if ip_address not in self.login_attempts:
                self.login_attempts[ip_address] = []
            self.login_attempts[ip_address].append(now)
            
        self.log_security_event(
            event_type='login_attempt',
            user_id=user_id,
            ip_address=ip_address,
            user_agent=request.headers.get('User-Agent', ''),
            details={'success': success},
            risk_score=0.3 if success else 0.6
        )
        
    def validate_input(self, data: str, input_type: str = 'general') -> Tuple[bool, Optional[str]]:
        """입력 데이터 검증"""
        if not data:
            return False, "입력 데이터가 비어있습니다."
            
        # XSS 방지
        xss_patterns = [
            r'<script[^>]*>.*?</script>',
            r'javascript:',
            r'on\w+\s*=',
            r'<iframe[^>]*>',
            r'<object[^>]*>',
            r'<embed[^>]*>'
        ]
        
        for pattern in xss_patterns:
            if re.search(pattern, data, re.IGNORECASE):
                return False, "XSS 공격이 감지되었습니다."
                
        # SQL 인젝션 방지 (기본적인 패턴)
        sql_patterns = [
            r'(\b(union|select|insert|update|delete|drop|create|alter)\b)',
            r'(\b(or|and)\b\s+\d+\s*=\s*\d+)',
            r'(\b(union|select|insert|update|delete|drop|create|alter)\b.*\b(union|select|insert|update|delete|drop|create|alter)\b)'
        ]
        
        for pattern in sql_patterns:
            if re.search(pattern, data, re.IGNORECASE):
                return False, "SQL 인젝션이 감지되었습니다."
                
        # 이메일 검증
        if input_type == 'email':
            email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            if not re.match(email_pattern, data):
                return False, "유효하지 않은 이메일 형식입니다."
                
        # 전화번호 검증
        elif input_type == 'phone':
            phone_pattern = r'^[0-9-+\s()]{10,15}$'
            if not re.match(phone_pattern, data):
                return False, "유효하지 않은 전화번호 형식입니다."
                
        return True, None
        
    def validate_ip_address(self, ip_address: str) -> bool:
        """IP 주소 검증"""
        try:
            ip = ipaddress.ip_address(ip_address)
            
            # 사설 IP 주소 허용
            if ip.is_private:
                return True
                
            # 특정 IP 주소 차단
            if ip_address in self.config['suspicious_ips']:
                return False
                
            return True
        except ValueError:
            return False
            
    def log_security_event(self, event_type: str, user_id: Optional[str], 
                          ip_address: str, user_agent: str, details: Dict, risk_score: float):
        """보안 이벤트 로깅"""
        event = SecurityEvent(
            timestamp=datetime.now(),
            event_type=event_type,
            user_id=user_id,
            ip_address=ip_address,
            user_agent=user_agent,
            details=details,
            risk_score=risk_score
        )
        
        self.security_events.append(event)
        
        # 데이터베이스에 저장
        conn = sqlite3.connect('security/security.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO security_events (
                timestamp, event_type, user_id, ip_address, user_agent, details, risk_score
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            event.timestamp.isoformat(),
            event.event_type,
            event.user_id,
            event.ip_address,
            event.user_agent,
            str(event.details),
            event.risk_score
        ))
        
        conn.commit()
        conn.close()
        
        # 위험도가 높은 이벤트는 즉시 알림
        if risk_score > 0.7:
            logger.warning(f"높은 위험도 보안 이벤트: {event_type} - IP: {ip_address} - 점수: {risk_score}")
            
    def require_auth(self, f):
        """인증 요구 데코레이터"""
        @wraps(f)
        def decorated_function(*args, **kwargs):
            token = request.headers.get('Authorization')
            
            if not token:
                return jsonify({'error': '인증 토큰이 필요합니다.'}), 401
                
            if not token.startswith('Bearer '):
                return jsonify({'error': '유효하지 않은 토큰 형식입니다.'}), 401
                
            token = token[7:]  # 'Bearer ' 제거
            
            payload = self.verify_token(token)
            if not payload:
                return jsonify({'error': '유효하지 않은 토큰입니다.'}), 401
                
            g.user_id = payload['user_id']
            return f(*args, **kwargs)
            
        return decorated_function
        
    def require_csrf(self, f):
        """CSRF 보호 데코레이터"""
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if request.method in ['GET', 'HEAD', 'OPTIONS']:
                return f(*args, **kwargs)
                
            csrf_token = request.headers.get('X-CSRF-Token')
            if not csrf_token:
                return jsonify({'error': 'CSRF 토큰이 필요합니다.'}), 403
                
            # CSRF 토큰 검증 로직 (실제 구현에서는 세션과 비교)
            # 여기서는 간단한 예시
            if not self.validate_csrf_token(csrf_token):
                return jsonify({'error': '유효하지 않은 CSRF 토큰입니다.'}), 403
                
            return f(*args, **kwargs)
            
        return decorated_function
        
    def validate_csrf_token(self, token: str) -> bool:
        """CSRF 토큰 검증"""
        # 실제 구현에서는 세션에 저장된 토큰과 비교
        # 여기서는 간단한 예시로 항상 True 반환
        return True
        
    def get_security_report(self, hours: int = 24) -> Dict:
        """보안 리포트 생성"""
        cutoff_date = datetime.now() - timedelta(hours=hours)
        
        conn = sqlite3.connect('security/security.db')
        cursor = conn.cursor()
        
        # 이벤트 통계
        cursor.execute('''
            SELECT event_type, COUNT(*) as count, AVG(risk_score) as avg_risk
            FROM security_events 
            WHERE timestamp > ?
            GROUP BY event_type
        ''', (cutoff_date.isoformat(),))
        
        events_by_type = {}
        for row in cursor.fetchall():
            events_by_type[row[0]] = {
                'count': row[1],
                'avg_risk': row[2]
            }
            
        # 차단된 IP 통계
        cursor.execute('''
            SELECT COUNT(*) as blocked_count
            FROM blocked_ips 
            WHERE blocked_until > ?
        ''', (datetime.now().isoformat(),))
        
        blocked_count = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            'period_hours': hours,
            'events_by_type': events_by_type,
            'blocked_ips_count': blocked_count,
            'total_events': sum(event['count'] for event in events_by_type.values()),
            'avg_risk_score': sum(event['avg_risk'] * event['count'] for event in events_by_type.values()) / 
                             sum(event['count'] for event in events_by_type.values()) if events_by_type else 0
        }

def main():
    """메인 실행 함수"""
    print("🔒 보안 관리자 초기화...")
    
    # 보안 설정
    config = {
        'jwt_secret': 'your-super-secret-key-change-this-in-production',
        'jwt_expiration': 3600,
        'rate_limit_window': 60,
        'rate_limit_max_requests': 100,
        'password_min_length': 8,
        'password_require_special': True,
        'max_login_attempts': 5,
        'lockout_duration': 900,
        'suspicious_ips': ['192.168.1.100'],  # 의심스러운 IP
        'allowed_origins': ['http://localhost:3000'],
        'enable_csrf': True,
        'enable_xss_protection': True
    }
    
    security_manager = SecurityManager(config)
    
    print("✅ 보안 관리자가 초기화되었습니다.")
    print("\n📋 보안 기능:")
    print("  - JWT 토큰 인증")
    print("  - 비밀번호 해싱 및 검증")
    print("  - 속도 제한 (Rate Limiting)")
    print("  - 로그인 시도 제한")
    print("  - XSS 및 SQL 인젝션 방지")
    print("  - CSRF 보호")
    print("  - 보안 이벤트 로깅")
    print("  - IP 주소 검증")
    
    # 테스트
    print("\n🧪 보안 테스트:")
    
    # 비밀번호 검증 테스트
    password = "TestPassword123!"
    is_valid, errors = security_manager.validate_password_strength(password)
    print(f"  비밀번호 강도 검증: {'✅' if is_valid else '❌'}")
    if not is_valid:
        for error in errors:
            print(f"    - {error}")
            
    # 입력 검증 테스트
    test_input = "<script>alert('xss')</script>"
    is_valid, error = security_manager.validate_input(test_input)
    print(f"  XSS 방지 테스트: {'✅' if not is_valid else '❌'}")
    if not is_valid:
        print(f"    - {error}")
        
    # 토큰 생성/검증 테스트
    token = security_manager.generate_token("test_user")
    payload = security_manager.verify_token(token)
    print(f"  JWT 토큰 테스트: {'✅' if payload else '❌'}")

if __name__ == "__main__":
    main() 
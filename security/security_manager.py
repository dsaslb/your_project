#!/usr/bin/env python3
"""
보안 강화 시스템
"""

import jwt
import bcrypt
import hashlib
import secrets
import time
from datetime import datetime, timedelta
from typing import Dict, Optional, List, Any
from dataclasses import dataclass
import logging

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class SecurityConfig:
    """보안 설정 클래스"""
    jwt_secret: str
    jwt_algorithm: str = "HS256"
    jwt_expiration_hours: int = 24
    password_min_length: int = 8
    max_login_attempts: int = 5
    lockout_duration_minutes: int = 30
    session_timeout_minutes: int = 60

@dataclass
class UserSession:
    """사용자 세션 정보"""
    user_id: str
    session_id: str
    created_at: datetime
    last_activity: datetime
    ip_address: str
    user_agent: str
    is_active: bool = True

@dataclass
class SecurityEvent:
    """보안 이벤트 정보"""
    event_id: str
    user_id: Optional[str]
    event_type: str
    description: str
    ip_address: str
    user_agent: str
    timestamp: datetime
    severity: str  # low, medium, high, critical
    status: str = "pending"  # pending, reviewed, resolved

class SecurityManager:
    """보안 관리자 클래스"""
    
    def __init__(self, config: SecurityConfig):
        self.config = config
        self.active_sessions: Dict[str, UserSession] = {}
        self.login_attempts: Dict[str, List[datetime]] = {}
        self.security_events: List[SecurityEvent] = []
        
    def generate_jwt_token(self, user_id: str, user_roles: List[str]) -> str:
        """JWT 토큰 생성"""
        try:
            payload = {
                'user_id': user_id,
                'roles': user_roles,
                'exp': datetime.utcnow() + timedelta(hours=self.config.jwt_expiration_hours),
                'iat': datetime.utcnow(),
                'jti': secrets.token_urlsafe(32)
            }
            token = jwt.encode(payload, self.config.jwt_secret, algorithm=self.config.jwt_algorithm)
            logger.info(f"JWT 토큰 생성 완료: user_id={user_id}")
            return token
        except Exception as e:
            logger.error(f"JWT 토큰 생성 실패: {e}")
            raise
    
    def verify_jwt_token(self, token: str) -> Optional[Dict[str, Any]]:
        """JWT 토큰 검증"""
        try:
            payload = jwt.decode(token, self.config.jwt_secret, algorithms=[self.config.jwt_algorithm])
            return payload
        except jwt.ExpiredSignatureError:
            logger.warning("JWT 토큰 만료됨")
            return None
        except jwt.InvalidTokenError as e:
            logger.warning(f"JWT 토큰 검증 실패: {e}")
            return None
    
    def hash_password(self, password: str) -> str:
        """비밀번호 해시화"""
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')
    
    def verify_password(self, password: str, hashed_password: str) -> bool:
        """비밀번호 검증"""
        return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))
    
    def validate_password_strength(self, password: str) -> Dict[str, Any]:
        """비밀번호 강도 검증"""
        errors = []
        warnings = []
        
        if len(password) < self.config.password_min_length:
            errors.append(f"비밀번호는 최소 {self.config.password_min_length}자 이상이어야 합니다")
        
        if not any(c.isupper() for c in password):
            warnings.append("대문자를 포함하는 것을 권장합니다")
        
        if not any(c.islower() for c in password):
            warnings.append("소문자를 포함하는 것을 권장합니다")
        
        if not any(c.isdigit() for c in password):
            warnings.append("숫자를 포함하는 것을 권장합니다")
        
        if not any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password):
            warnings.append("특수문자를 포함하는 것을 권장합니다")
        
        return {
            'is_valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings,
            'score': self._calculate_password_score(password)
        }
    
    def _calculate_password_score(self, password: str) -> int:
        """비밀번호 강도 점수 계산 (0-100)"""
        score = 0
        
        # 길이 점수
        if len(password) >= 8:
            score += 20
        if len(password) >= 12:
            score += 10
        
        # 문자 종류 점수
        if any(c.isupper() for c in password):
            score += 15
        if any(c.islower() for c in password):
            score += 15
        if any(c.isdigit() for c in password):
            score += 15
        if any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password):
            score += 15
        
        # 복잡성 점수
        if len(set(password)) >= len(password) * 0.8:
            score += 10
        
        return min(score, 100)
    
    def create_session(self, user_id: str, ip_address: str, user_agent: str) -> str:
        """사용자 세션 생성"""
        session_id = secrets.token_urlsafe(32)
        session = UserSession(
            user_id=user_id,
            session_id=session_id,
            created_at=datetime.utcnow(),
            last_activity=datetime.utcnow(),
            ip_address=ip_address,
            user_agent=user_agent
        )
        self.active_sessions[session_id] = session
        logger.info(f"세션 생성: user_id={user_id}, session_id={session_id}")
        return session_id
    
    def validate_session(self, session_id: str) -> Optional[UserSession]:
        """세션 검증"""
        if session_id not in self.active_sessions:
            return None
        
        session = self.active_sessions[session_id]
        
        # 세션 만료 확인
        if datetime.utcnow() - session.last_activity > timedelta(minutes=self.config.session_timeout_minutes):
            self.invalidate_session(session_id)
            return None
        
        # 활동 시간 업데이트
        session.last_activity = datetime.utcnow()
        return session
    
    def invalidate_session(self, session_id: str):
        """세션 무효화"""
        if session_id in self.active_sessions:
            del self.active_sessions[session_id]
            logger.info(f"세션 무효화: session_id={session_id}")
    
    def track_login_attempt(self, user_id: str, ip_address: str, success: bool):
        """로그인 시도 추적"""
        if user_id not in self.login_attempts:
            self.login_attempts[user_id] = []
        
        self.login_attempts[user_id].append(datetime.utcnow())
        
        # 오래된 시도 제거
        cutoff_time = datetime.utcnow() - timedelta(minutes=self.config.lockout_duration_minutes)
        self.login_attempts[user_id] = [
            attempt for attempt in self.login_attempts[user_id] 
            if attempt > cutoff_time
        ]
        
        # 보안 이벤트 기록
        event_type = "login_success" if success else "login_failed"
        severity = "medium" if success else "high"
        description = f"로그인 {'성공' if success else '실패'}: {user_id}"
        
        self.log_security_event(
            user_id=user_id,
            event_type=event_type,
            description=description,
            ip_address=ip_address,
            user_agent="",
            severity=severity
        )
    
    def is_account_locked(self, user_id: str) -> bool:
        """계정 잠금 상태 확인"""
        if user_id not in self.login_attempts:
            return False
        
        recent_attempts = [
            attempt for attempt in self.login_attempts[user_id]
            if datetime.utcnow() - attempt < timedelta(minutes=self.config.lockout_duration_minutes)
        ]
        
        return len(recent_attempts) >= self.config.max_login_attempts
    
    def log_security_event(self, user_id: Optional[str], event_type: str, 
                          description: str, ip_address: str, user_agent: str, 
                          severity: str = "medium"):
        """보안 이벤트 기록"""
        event = SecurityEvent(
            event_id=secrets.token_urlsafe(16),
            user_id=user_id,
            event_type=event_type,
            description=description,
            ip_address=ip_address,
            user_agent=user_agent,
            timestamp=datetime.utcnow(),
            severity=severity
        )
        self.security_events.append(event)
        logger.info(f"보안 이벤트 기록: {event_type} - {description}")
    
    def get_security_events(self, user_id: Optional[str] = None, 
                           event_type: Optional[str] = None,
                           severity: Optional[str] = None,
                           limit: int = 100) -> List[SecurityEvent]:
        """보안 이벤트 조회"""
        events = self.security_events
        
        if user_id:
            events = [e for e in events if e.user_id == user_id]
        if event_type:
            events = [e for e in events if e.event_type == event_type]
        if severity:
            events = [e for e in events if e.severity == severity]
        
        # 최신 순으로 정렬
        events.sort(key=lambda x: x.timestamp, reverse=True)
        return events[:limit]
    
    def cleanup_expired_sessions(self):
        """만료된 세션 정리"""
        current_time = datetime.utcnow()
        expired_sessions = []
        
        for session_id, session in self.active_sessions.items():
            if current_time - session.last_activity > timedelta(minutes=self.config.session_timeout_minutes):
                expired_sessions.append(session_id)
        
        for session_id in expired_sessions:
            self.invalidate_session(session_id)
        
        if expired_sessions:
            logger.info(f"만료된 세션 {len(expired_sessions)}개 정리 완료")
    
    def get_security_stats(self) -> Dict[str, Any]:
        """보안 통계 조회"""
        current_time = datetime.utcnow()
        last_24h = current_time - timedelta(hours=24)
        
        recent_events = [
            e for e in self.security_events 
            if e.timestamp > last_24h
        ]
        
        failed_logins = [
            e for e in recent_events 
            if e.event_type == "login_failed"
        ]
        
        return {
            'active_sessions': len(self.active_sessions),
            'total_events_24h': len(recent_events),
            'failed_logins_24h': len(failed_logins),
            'locked_accounts': len([
                user_id for user_id in self.login_attempts 
                if self.is_account_locked(user_id)
            ]),
            'security_score': self._calculate_security_score()
        }
    
    def _calculate_security_score(self) -> int:
        """보안 점수 계산 (0-100)"""
        score = 100
        
        # 실패한 로그인 시도에 따른 감점
        total_failed_attempts = sum(len(attempts) for attempts in self.login_attempts.values())
        if total_failed_attempts > 10:
            score -= min(total_failed_attempts * 2, 30)
        
        # 잠긴 계정에 따른 감점
        locked_accounts = len([
            user_id for user_id in self.login_attempts 
            if self.is_account_locked(user_id)
        ])
        score -= locked_accounts * 5
        
        # 높은 심각도의 보안 이벤트에 따른 감점
        critical_events = [
            e for e in self.security_events 
            if e.severity == "critical" and 
            e.timestamp > datetime.utcnow() - timedelta(hours=24)
        ]
        score -= len(critical_events) * 10
        
        return max(score, 0) 